class ConfigLoader:
    def __init__(self, config_file):
        """
        用于加载配置文件中的信息以设置bot运行的各种参数
        :param config_file: 配置文件的路径
        """
        self.config_file = config_file
        ...

    def bot_init_loader(self):
        """
        当bot初始化时，调用一次该方法，用于从配置文件中加载bot的初始参数
        :return: 加载的所有配置信息，以字典的形式返回
        """
        ...

    def plugins_config_loader(self):
        """
        在bot运行期间，持续加载配置文件中的关于每个插件的配置参数
        :return: 加载的所有配置信息，以字典的形式返回
        """
        ...
