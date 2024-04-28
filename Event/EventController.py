import logging
from flask import Flask, request
import asyncio
from threading import Thread

from Event.EventHandler.GroupMessageEventHandler import GroupMessageEvent
from Event.EventHandler.PrivateMessageEventHandler import PrivateMessageEvent
from Logging.PrintLog import Log
from Plugins import Plugins
from ConfigLoader.ConfigLoader import ConfigLoader
log = Log()


class Event:
    flask_log = logging.getLogger('werkzeug')
    flask_log.setLevel(logging.ERROR)

    def __init__(self, plugins_list: list[Plugins], config_loader: ConfigLoader, debug:bool):
        try:
            self.app = Flask(__name__)
            self.debug = debug
            self.register_routes()
            self.plugins_list = plugins_list
            self.plugins_config = None
            self.config_loader = config_loader
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

            # 每次收到事件时都更新一次插件配置
            self.config_loader.plugins_config_loader()
            self.plugins_config = self.config_loader.get("Plugins", "dict")

            # 根据post_type处理不同类型的上报消息
            if post_type == "message":
                message_type = data.get("message_type")
                if message_type == "private":
                    event = PrivateMessageEvent(data)
                    event.post_event(self.debug)
                    thread = Thread(target=self.handle_private_message, args=(event,))
                    thread.start()
                elif message_type == "group":
                    event = GroupMessageEvent(data)
                    event.post_event(self.debug)
                    thread = Thread(target=self.handle_group_message, args=(event,))
                    thread.start()

            elif post_type == "notice":
                ...

            return 'OK', 200  # 返回成功的响应

    def handle_private_message(self, event):
        asyncio.run(self.run_private_plugins(event))

    async def run_private_plugins(self, event):
        for plugins in self.plugins_list:
            plugins_type = plugins.type
            plugins_name = plugins.name
            plugins_author = plugins.author
            if plugins_type == "Private":
                try:
                    config = self.plugins_config.get(plugins_name)
                    # config = {"enable": True}
                    await plugins.main(event, self.debug, config)
                except Exception as e:
                    log.error(f"插件：{plugins_name}运行时出错：{e}，请联系该插件的作者：{plugins_author}")

    def handle_group_message(self, event):
        asyncio.run(self.run_group_plugins(event))

    async def run_group_plugins(self, event):
        for plugins in self.plugins_list:
            plugins_type = plugins.type
            plugins_name = plugins.name
            plugins_author = plugins.author
            if plugins_type == "Group":
                try:
                    config = self.plugins_config.get(plugins_name)
                    # config = {"enable": True}
                    await plugins.main(event, self.debug, config)
                except Exception as e:
                    log.error(f"插件：{plugins_name}运行时出错：{e}，请联系该插件的作者：{plugins_author}")

