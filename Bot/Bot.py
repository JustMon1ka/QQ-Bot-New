from Plugins import plugins_path
from Event.EventController import Event
from Interface.Api import Api
from Logging.PrintLog import Log

from importlib import import_module
from pkgutil import iter_modules
import logging

log = Log()


class Bot:
    def __init__(self, server_address, client_address, debug):
        """
        初始化bot对象
        :param server_address: bot监听端启用的ip地址和端口
        :param client_address: bot插件端的消息接收ip地址和端口
        """
        try:
            # 成员变量初始化
            self.server_address = server_address
            self.client_address = client_address
            self.debug = debug

            # 成员对象初始化
            self.api = Api(server_address)

            # 初始化插件列表
            self.plugins_list = []

        except Exception as e:
            raise e

    async def initialize(self):
        """
        异步地完成Bot对象的初始化
        """
        try:
            login_info = await self.api.botSelfInfo.get_login_info()
            log.info(f"获取到Bot的登录信息：{login_info}")
            log.info("Bot初始化成功！")
            self.init_plugins()
        except Exception as e:
            log.error(e)

    def init_plugins(self):
        """
        初始化所有添加了的插件
        :return:
        """
        for _, name, ispkg in iter_modules([plugins_path]):
            if not ispkg:
                continue  # 如果不是插件包就跳过

            try:
                # 从Plugins包动态导入子包
                plugin_module = import_module(f".{name}", 'Plugins')
                # 获取子包中的插件类，假设类名与模块名相同
                PluginClass = getattr(plugin_module, name)
                # 实例化插件
                plugin_instance = PluginClass(self.server_address)
                # 添加到插件列表
                self.plugins_list.append(plugin_instance)
                log.info(f"成功加载插件：{plugin_instance.name}，插件类型：{plugin_instance.type}")
            except Exception as e:
                log.error(f"加载插件{name}失败：{e}")

    def run(self):
        self.event = Event(self.plugins_list, self.debug)
        ip_address, port = self.client_address.split(":")
        # 使用Flask实例的run方法启动Flask服务
        log.info("启动Flask监听服务")
        self.event.app.run(host=ip_address, port=int(port), debug=False)


if __name__ == "__main__":
    server_address = "120.26.217.8:5700"
    client_address = "0.0.0.0:7000"
    bot = Bot(server_address, client_address, True)
    bot.run()
