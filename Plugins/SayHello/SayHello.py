from Event.EventHandler.PrivateMessageEventHandler import PrivateMessageEvent
from Interface.Api import Api
from Logging.PrintLog import Log
log = Log()


class SayHello:
    """
    插件名：say_hello_private
    插件类型：私聊插件
    插件功能：当有人通过私聊向bot发送“Hello”时，bot会自动回复一个Hello消息
    """
    def __init__(self, server_address):
        self.server_address = server_address
        self.api = Api(server_address)
        self.name = "say_hello_private"
        self.type = "Private"

    async def main(self, event: PrivateMessageEvent, debug, config):
        enable = config.get("enable")
        if not enable:
            return

        message = event.message
        if message == "Hello":
            user_id = event.user_id
            nickname = event.nickname
            reply_message = f"Hello！{nickname}！"
            try:
                await self.api.privateService.send_private_msg(user_id, reply_message)
            except Exception as e:
                log.error(f"插件：{self.name}运行时出错：{e}")
            else:
                if debug:
                    log.debug(f"插件：{self.name}运行正确，成功向{user_id}发送了一条消息：{reply_message}")

