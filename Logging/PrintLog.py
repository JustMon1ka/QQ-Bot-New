import logging
from colorama import Fore, Style, init
init(autoreset=True)  # 初始化colorama并设置自动重置

# 创建一个日志格式器，指定时间、级别和消息
formatter = logging.Formatter(
    f"%(asctime)s [{Fore.BLUE}%(levelname)s{Style.RESET_ALL}] %(message)s",
    datefmt="%Y.%m.%d-%H:%M:%S"
)

# 创建一个流处理器并设置格式器
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)


# 自定义级别的颜色输出
class ColoredLevelFormatter(logging.Formatter):
    level_colors = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
    }

    def format(self, record):
        color = self.level_colors.get(record.levelname, Fore.WHITE)
        # 将消息部分应用相同的颜色
        record.msg = color + record.msg + Style.RESET_ALL
        return logging.Formatter.format(self, record)

# 使用自定义的颜色格式器
stream_handler.setFormatter(ColoredLevelFormatter(
    f"%(asctime)s [{Fore.BLUE}%(levelname)s{Style.RESET_ALL}] %(message)s",
    datefmt="%Y.%m.%d-%H:%M:%S"
))

# 创建日志记录器，设置级别，并添加处理器
logger = logging.getLogger("ColoredLogger")
logger.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)


class Log:
    def debug(self, message):
        logger.debug(message)

    def info(self, message):
        logger.info(message)

    def warning(self, message):
        logger.warning(message)

    def error(self, message):
        logger.error(message)