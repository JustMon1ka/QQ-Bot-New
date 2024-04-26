import logging
from flask import Flask, request
import asyncio
from threading import Thread

from Event.EventHandler.PrivateMessageEventHandler import PrivateMessageEvent
from Logging.PrintLog import Log
log = Log()


class Event:
    flask_log = logging.getLogger('werkzeug')
    flask_log.setLevel(logging.ERROR)

    def __init__(self, plugins_list, debug):
        try:
            self.app = Flask(__name__)
            self.debug = debug
            self.register_routes()
            self.plugins_list = plugins_list
            self.plugins_config = None
        except Exception as e:
            log.error(f"初始化事件处理器时失败：{e}")
            raise e
        else:
            log.info("初始化事件处理器成功！")

    def register_routes(self):
        # 使用self.app.route注册路由
        @self.app.route("/onebot", methods=["POST", "GET"])
        def post_data():
            data = request.get_json()
            post_type = data.get("post_type")
            self.plugins_config = ...
            # 根据post_type处理不同类型的上报消息
            if post_type == "message":
                message_type = data.get("message_type")
                if message_type == "private":
                    event = PrivateMessageEvent(data)
                    if self.debug:
                        event.post_event()
                    thread = Thread(target=self.handle_private_message, args=(event,))
                    thread.start()
                elif message_type == "group":
                    ...
            elif post_type == "notice":
                ...

            return 'OK', 200  # 返回成功的响应

    def handle_private_message(self, event):
        asyncio.run(self.run_private_plugins(event))

    async def run_private_plugins(self, event):
        for plugins in self.plugins_list:
            plugins_type = plugins.type
            plugins_name = plugins.name
            if plugins_type == "Private":
                try:
                    # config = self.config.get(plugins_name)
                    config = {"enable": True}
                    await plugins.main(event, self.debug, config)
                except Exception as e:
                    log.error(f"插件：{plugins_name}运行时出错：{e}")

