from Event.EventHandler.PrivateMessageEventHandler import PrivateMessageEvent
from Logging.PrintLog import Log
from Plugins import Plugins
log = Log()


class SayHello(Plugins):
    """
    插件名：SayHello \n
    插件类型：私聊插件 \n
    插件功能：当有人通过私聊向bot发送“Hello”时，bot会自动回复一个Hello消息 \n
    这是一个简单的示例插件，可供后续插件的开发做参考
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "SayHello"
        self.type = "Private"
        self.author = "just monika"
        self.introduction = """
                                插件描述：自动回复Hello，可以用来检测bot是否存活
                                插件功能：当有人通过私聊向bot发送“Hello”时，bot会自动回复一个Hello消息
                            """
        self.init_status()

    async def main(self, event: PrivateMessageEvent, debug):
        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")
        message = event.message
        if message == "Hello":
            user_id = event.user_id
            reply_message = self.config.get("reply")
            try:
                await self.api.privateService.send_private_msg(user_id, reply_message)
            except Exception as e:
                log.error(f"插件：{self.name}运行时出错：{e}")
            else:
                log.debug(f"插件：{self.name}运行正确，成功向{user_id}发送了一条消息：{reply_message}", debug)

