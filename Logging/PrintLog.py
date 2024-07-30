import logging
import os
from logging.handlers import RotatingFileHandler

from colorama import Fore, Style, init

init(autoreset=True)  # 初始化colorama并设置自动重置

# 初始化colorama以支持控制台彩色输出
init(autoreset=True)


# 控制台输出的彩色格式器
class ColoredConsoleFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record):
        level_color = self.COLORS.get(record.levelno, Fore.WHITE)
        record.msg = f"{level_color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)


class SpecificLoggerFilter(logging.Filter):
    def __init__(self, logger_names):
        super().__init__()
        self.logger_names = logger_names

    def filter(self, record):
        return record.name in self.logger_names


# 创建控制台logger
def setup_console_logger():
    console_logger = logging.getLogger('ConsoleLogger')
    console_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_formatter = ColoredConsoleFormatter('%(asctime)s - [%(levelname)s] - %(message)s',
                                                datefmt='%Y.%m.%d-%H:%M:%S')
    console_handler.setFormatter(console_formatter)
    console_logger.addHandler(console_handler)
    return console_logger


log_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_file_path = os.path.join(log_directory, 'log.out')


# 创建文件logger
def setup_file_logger():
    file_logger = logging.getLogger('FileLogger')
    file_logger.setLevel(logging.DEBUG)
    file_handler = RotatingFileHandler(log_file_path, maxBytes=1024 * 1024 * 5, backupCount=5)
    file_formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s', datefmt='%Y.%m.%d-%H:%M:%S')
    file_handler.setFormatter(file_formatter)
    file_logger.addHandler(file_handler)
    return file_logger


# 实例化两个logger
console_logger = setup_console_logger()
file_logger = setup_file_logger()

flask_logger = logging.getLogger('werkzeug')
flask_logger.addFilter(SpecificLoggerFilter(['ConsoleLogger', 'FileLogger']))


class Log:
    @classmethod
    def debug(cls, message, debug=False):
        if debug:
            console_logger.debug(message)
            file_logger.debug(message)

    @classmethod
    def info(cls, message):
        console_logger.info(message)
        file_logger.info(message)

    @classmethod
    def warning(cls, message):
        console_logger.warning(message)
        file_logger.warning(message)

    @classmethod
    def error(cls, message):
        console_logger.error(message)
        file_logger.error(message)

    def start_logging(self):
        with open(log_file_path, "w") as f:
            ...

# 使用
if __name__ == "__main__":
    console_logger.info("这是一个彩色的控制台信息")
    file_logger.info("这是一个纯文本文件信息")


