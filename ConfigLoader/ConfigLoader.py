import configparser


class ConfigLoader:
    def __init__(self, config_file):
        """
        用于加载配置文件中的信息以设置bot运行的各种参数
        :param config_file: 配置文件的路径
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        # 显式地使用 UTF-8 编码打开配置文件
        self.init_config = {}
        self.plugins_config = {}

    def bot_init_loader(self):
        """
        当bot初始化时，调用一次该方法，用于从配置文件中加载bot的初始参数
        :return: 加载的所有配置信息，以字典的形式返回
        """
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config.read_file(f)

        init_config = {}
        if 'Init' in self.config:
            for key in self.config['Init']:
                init_config[key] = self.config['Init'][key]
                self.init_config[key] = self.config['Init'][key]
        else:
            raise ValueError("配置文件中必须有 [Init] 项。")
        return init_config

    def get_init_config(self, key, data_type):
        """
        获取bot初始化信息中指定键对应的值，如果这个键，则返回None
        :param key: 需要获取的配置键名。
        :param data_type: 返回值的类型，可选 'str', 'int', 'float', 'bool'。
        :return:
        """
        value = self.init_config.get(key)
        return self.get_config(value, data_type)

    def get_config(self, value, data_type):
        if value is None:
            return None

        try:
            if data_type == "dict":
                return value
            if data_type == 'bool':
                # 处理布尔值转换
                return eval(value)
            elif data_type == 'int':
                # 转换为整数
                return int(value)
            elif data_type == 'float':
                # 转换为浮点数
                return float(value)
            else:
                # 默认作为字符串返回
                return value
        except ValueError:
            # 类型转换失败时返回 None
            return None

