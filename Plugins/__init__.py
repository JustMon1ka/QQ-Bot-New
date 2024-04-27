# Plugins/__init__.py
import os
from Interface.Api import Api

# 获取当前目录的路径
plugins_path = os.path.dirname(__file__)


class Plugins:
    """
    插件的父类，所有编写的插件都继承这个类
    """
    def __init__(self, server_address):
        self.server_address = server_address
        self.api = Api(server_address)
        self.name = "name"
        self.type = "type"

    def main(self, event, debug, config):
        raise NotImplementedError("方法还未实现")
