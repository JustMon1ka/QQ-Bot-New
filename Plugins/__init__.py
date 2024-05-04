# Plugins/__init__.py
import os

from Interface.Api import Api

# 获取当前目录的路径
plugins_path = os.path.dirname(__file__)


class Plugins:
    """
    插件的父类，所有编写的插件都继承这个类
    """
    def __init__(self, server_address: str, bot):
        self.server_address = server_address
        self.api = Api(server_address)
        self.bot = bot
        self.name = "name"
        self.type = "type"
        self.author = "xxx"
        self.introduction = "xxx"
        self.status = None  # running/disable/error
        self.error_info = ""

    def main(self, event, debug, config):
        raise NotImplementedError("方法还未实现")

    def set_status(self, status: str, error_info: str = ""):
        """
        自带方法，设置该插件的运行情况
        :param error_info: 如果状态为error，在此处写明报错原因
        :param status: 可选参数：running, disable, error
        :return:
        """
        self.status = status
        self.error_info = error_info

    def init_status(self):
        """
        在初始化插件对象的时候加载配置文件中的enable信息，初始只设置为running或者disable
        :param:
        :return: True or False
        """
        # 使用安全的方式来解析字符串为布尔值
        enable_config = self.bot.configLoader.get_plugins_config(self.name, "dict").get("enable")
        enable_bool = enable_config.strip().lower() == 'true'
        self.status = "running" if enable_bool else "disable"
