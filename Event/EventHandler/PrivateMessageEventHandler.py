from Logging.PrintLog import Log
log = Log()


class PrivateMessageEvent:
    def __init__(self, data):
        sender = data.get("sender")
        self.user_id = sender.get("user_id")
        self.nickname = sender.get("nickname")
        self.raw_message = data.get("raw_message")
        self.message = data.get("message")
        ...

    def post_event(self, debug):
        log.debug(f"收到来自好友 {self.nickname}({self.user_id}) 的私聊消息：{self.message}", debug)