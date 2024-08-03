import logging
from multiprocessing import Process
import traceback
from flask import Flask, request
import asyncio
from threading import Thread
from gevent.pywsgi import WSGIServer

from Event.EventHandler.GroupMessageEventHandler import GroupMessageEvent
from Event.EventHandler.PrivateMessageEventHandler import PrivateMessageEvent
from Event.EventHandler.NoticeEventHandler import GroupRecallEvent
from Logging.PrintLog import Log
from Plugins import Plugins
from ConfigLoader.ConfigLoader import ConfigLoader

log = Log()


# 全局启动 Flask 应用的函数
def create_event_app(event_controller):
    app = Flask("Event Controller")

    @app.route("/onebot", methods=["POST", "GET"])
    def post_data():
        data = request.get_json()
        post_type = data.get("post_type")

        if post_type == "message":
            message_type = data.get("message_type")
            if message_type == "private":
                event = PrivateMessageEvent(data)
                event.post_event(event_controller.debug)
                thread = Thread(target=event_controller.handle_private_message, args=(event,))
                thread.start()
            elif message_type == "group":
                event = GroupMessageEvent(data)
                event.post_event(event_controller.debug)
                thread = Thread(target=event_controller.handle_group_message, args=(event,))
                thread.start()
        elif post_type == "notice":
            notice_type = data.get("notice_type")
            if notice_type == "group_recall":
                event = GroupRecallEvent(data)
                event.post_event(event_controller.debug)
                thread = Thread(target=event_controller.handle_group_recall, args=(event,))
                thread.start()
            else:
                ...

        return 'OK', 200

    app.logger.setLevel(logging.ERROR)
    return app


class Event:
    flask_log = logging.getLogger('werkzeug')
    flask_log.setLevel(logging.ERROR)

    def __init__(self, plugins_list: list[Plugins], config_loader: ConfigLoader, debug: bool):
        try:
            self.debug = debug
            self.plugins_list = plugins_list
            self.config_loader = config_loader
        except Exception as e:
            log.error(f"初始化事件处理器时失败：{e}")
            raise e
        else:
            log.info("初始化事件处理器成功！")

    # 创建一个不记录任何内容的日志器
    class SilentLogger(object):
        def __init__(self):
            self.allowed_loggers = ['ConsoleLogger', 'FileLogger']
            self.console_logger = logging.getLogger('ConsoleLogger')
            self.file_logger = logging.getLogger('FileLogger')

        def write(self, message):
            # 过滤并只记录来自自定义日志记录器的消息
            if any(logger_name in message for logger_name in self.allowed_loggers):
                if message.strip():  # 过滤空消息
                    self.console_logger.info(message.strip())
                    self.file_logger.info(message.strip())

        def flush(self):
            pass

    def run(self, ip, port):
        # 启动新进程运行 Flask 应用
        app = create_event_app(self)
        server = WSGIServer((ip, port), app, log=self.SilentLogger(), error_log=self.SilentLogger())
        # server = WSGIServer((ip, port), app)
        server.serve_forever()

    def handle_private_message(self, event):
        asyncio.run(self.run_private_plugins(event))

    async def run_private_plugins(self, event):
        for plugins in self.plugins_list:
            plugins_type = plugins.type
            plugins_name = plugins.name
            plugins_author = plugins.author
            if plugins_type == "Private":
                try:
                    plugins.load_config()
                    await plugins.main(event, self.debug)
                except Exception as e:
                    traceback_info = traceback.format_exc()
                    error_info = f"插件：{plugins_name}运行时出错：{e}，请联系该插件的作者：{plugins_author}\n详细信息：\n{traceback_info}"
                    plugins.set_status("error", error_info)
                    log.error(error_info)

    def handle_group_message(self, event):
        asyncio.run(self.run_group_plugins(event))

    async def run_group_plugins(self, event):
        for plugins in self.plugins_list:
            plugins_type = plugins.type
            plugins_name = plugins.name
            plugins_author = plugins.author
            if plugins_type == "Group":
                try:
                    plugins.load_config()
                    await plugins.main(event, self.debug)
                except Exception as e:
                    traceback_info = traceback.format_exc()
                    error_info = f"插件：{plugins_name}运行时出错：{e}，请联系该插件的作者：{plugins_author}\n详细信息：\n{traceback_info}"
                    plugins.set_status("error", error_info)
                    log.error(error_info)
    
    def handle_group_recall(self, event):
        asyncio.run(self.run_group_recall(event))

    async def run_group_recall(self, event):
        for plugins in self.plugins_list:
            plugins_type = plugins.type
            plugins_name = plugins.name
            plugins_author = plugins.author
            if plugins_type == "GroupRecall":
                try:
                    plugins.load_config()
                    await plugins.main(event, self.debug)
                except Exception as e:
                    traceback_info = traceback.format_exc()
                    error_info = f"插件：{plugins_name}运行时出错：{e}，请联系该插件的作者：{plugins_author}\n详细信息：\n{traceback_info}"
                    plugins.set_status("error", error_info)
                    log.error(error_info)

# 示例用法
if __name__ == "__main__":
    plugins_list = []  # 假设的插件列表
    config_loader = None  # 假设的配置加载器
    event = Event(plugins_list, config_loader, debug=True)
    event.run('127.0.0.1', 5000, False)
