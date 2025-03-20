from Logging.PrintLog import Log
from Plugins import Plugins
log=Log()

class DailyWord(Plugins):
    """
    这是一个插件的模板，开发一个新的插件至少应该包含以下部分
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "DailyWord"  # 插件的名字（一定要和类的名字完全一致（主要是我能力有限，否则会报错））
        self.type = "Private"  # 插件的类型（这个插件是在哪种消息类型中触发的）
        self.author = "x1x"  # 插件开发作者（不用留真名，但是当插件报错的时候需要根据这个名字找到对应的人来修）
        self.introduction = """
                                每日一词小程序^_^
                            """
        self.init_status()

    async def main(self, event, debug):
        """
        函数的入口，每个插件都必须有一个主入口 \n
        受到框架限制，所有插件的main函数的参数必须是这几个，不能多也不能少 \n
        注意！所有的插件都需要写成异步的方法，防止某个插件出问题卡死时导致整个程序阻塞
        :param event: 消息事件体
        :param debug: 是否输出debug信息
        :return:
        """
        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")

        message = event.message
        user_id = event.user_id
        reply_message = "hello"
        try:
            self.api.privateService.send_private_msg(user_id, reply_message)
        except Exception as e:
            log.error(f"插件：{self.name}运行时出错：{e}")
        else:
            log.debug(f"插件：{self.name}运行正确，成功向{user_id}发送了一条消息：{reply_message}", debug)

        return