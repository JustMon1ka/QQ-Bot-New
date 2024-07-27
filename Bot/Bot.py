from importlib import import_module
from pkgutil import iter_modules
from sqlalchemy.ext.asyncio import create_async_engine
from gevent import spawn, joinall
import logging

from ConfigLoader.ConfigLoader import ConfigLoader
from Event.EventController import Event
from Interface.Api import Api
from Logging.PrintLog import Log
from Plugins import plugins_path, Plugins
from WebController.WebController import WebController

log = Log()


# 全局定义 run_service 函数
def run_service(service, host, port, debug):
    service.run(ip=host, port=port, debug=debug)


class Bot:
    def __init__(self, config_file: str):
        """
        初始化bot对象
        :param config_file: 配置文件的路径（绝对/相对）
        """
        log.start_logging()
        try:
            # 成员变量初始化
            self.config_file: str = config_file

            # 初始化配置加载器
            self.configLoader: ConfigLoader = ConfigLoader(config_file)

            # 初始化插件列表
            self.plugins_list: list[Plugins] = []

            # 初始化数据库连接对象
            self.database = None

            # 通过configLoader加载其他初始化参数
            log.info(f"开始加载Bot配置文件，文件路径：{self.config_file}")
            init_config = self.configLoader.bot_init_loader()

            # 需要检查的关键配置项
            required_configs = {
                "server_address": self.configLoader.get_init_config("server_address", "str"),
                "client_address": self.configLoader.get_init_config("client_address", "str"),
                "web_controller": self.configLoader.get_init_config("web_controller", "str"),
                "bot_name": self.configLoader.get_init_config("bot_name", "str"),
                "debug": self.configLoader.get_init_config("debug", "bool"),
                "database_enable": self.configLoader.get_init_config("database_enable", "bool"),
                "database_username": self.configLoader.get_init_config("database_username", "str"),
                "database_address": self.configLoader.get_init_config("database_address", "str"),
                "database_passwd": self.configLoader.get_init_config("database_passwd", "str"),
                "database_name": self.configLoader.get_init_config("database_name", "str"),
            }

            # 检查哪些关键配置项是空的
            missing_configs = [key for key, value in required_configs.items() if value is None]
            if missing_configs:
                raise ValueError(f"参数不全，以下配置项未成功加载：{', '.join(missing_configs)}")

            # 将配置值分配给实例变量
            self.server_address = required_configs["server_address"]
            self.client_address = required_configs["client_address"]
            self.web_controller = required_configs["web_controller"]
            self.bot_name = required_configs["bot_name"]
            self.debug = required_configs["debug"]
            self.database_enable = required_configs["database_enable"]
            self.database_username = required_configs["database_username"]
            self.database_address = required_configs["database_address"]
            self.database_passwd = required_configs["database_passwd"]
            self.database_name = required_configs["database_name"]

            log.info(f"成功加载配置文件")
            log.info(f"加载的bot初始化配置信息如下：")
            for item in init_config.items():
                log.info(str(item))

            # 初始化api接口对象
            self.api = Api(self.server_address)

        except Exception as e:
            raise e

    async def initialize(self):
        """
        异步地完成Bot对象的初始化
        """
        try:
            login_info = await self.api.botSelfInfo.get_login()
            log.info(f"获取到Bot的登录信息：{login_info}")
            log.info("Bot初始化成功！")
            self.init_plugins()
            await self.init_database()
        except Exception as e:
            log.error(f"初始化Bot时失败：{e}")
            raise e

    async def init_database(self):
        """
        创建与数据库之间的连接
        :return:
        """
        if not self.database_enable:
            log.info("初始化配置{database_enable}项为：False，将不尝试连接数据库")
            self.database = None
            return
        log.info("开始创建与数据库之间的连接")
        try:
            self.database = create_async_engine(f'mysql+aiomysql://'
                                                f'{self.database_username}:{self.database_passwd}@{self.database_address}/{self.database_name}')
            log.info("成功连接到bot数据库")
        except Exception as e:
            log.error(f"连接到数据库时失败：{e}")
            raise e

    def init_plugins(self):
        """
        初始化所有添加了的插件
        :return:
        """
        log.info("开始加载插件")

        for _, name, ispkg in iter_modules([plugins_path]):
            if not ispkg:
                continue  # 如果不是插件包就跳过

            try:
                # 从Plugins包动态导入子包
                plugin_module = import_module(f".{name}", 'Plugins')
                # 获取子包中的插件类，假设类名与模块名相同
                PluginClass = getattr(plugin_module, name)
                # 实例化插件
                plugin_instance: Plugins = PluginClass(self.server_address, self)
                plugin_instance.load_config()
                # 添加到插件列表
                self.plugins_list.append(plugin_instance)
                log.info(
                    f"成功加载插件：{plugin_instance.name}，插件类型：{plugin_instance.type}，插件作者{plugin_instance.author}")
            except Exception as e:
                log.error(f"加载插件{name}失败：{e}")
                raise e

    def run(self):
        event = Event(self.plugins_list, self.configLoader, self.debug)
        ip_address, port = self.client_address.split(":")
        # 使用Flask实例的run方法启动Flask服务
        log.info(f"尝试将监听服务启动在 {ip_address}:{port}")
        event_server = spawn(event.run, ip_address, int(port))
        log.info("监听服务启动成功！")

        webController = WebController(self)
        ip_address, port = self.web_controller.split(":")
        # 使用Flask实例的run方法启动Flask服务
        log.info(f"启动web controller服务 {ip_address}:{port}")
        web_server = spawn(webController.run, ip_address, int(port))
        log.info("web controller服务启动成功！")
        # log.error("TEST ERROR")

        joinall([event_server, web_server])


if __name__ == "__main__":
    ...
