from Logging.PrintLog import Log
log = Log()


class GroupMessageEvent:
    """
    {'self_id': 2480365135, 'user_id': 1664382962, 'time': 1714299997, 'message_id': -2147471991,
    'real_id': -2147471991, 'message_type': 'group', 'sender': {'user_id': 1664382962, 'nickname': '\u3000\u3000',
    'card': '2252321-信10-易铭骏', 'role': 'admin'}, 'raw_message': '123', 'font': 14, 'sub_type': 'normal',
    'message': '123', 'message_format': 'string', 'post_type': 'message', 'group_id': 824395694}
    """
    def __init__(self, data):
        sender = data.get("sender")
        self.user_id: int = sender.get("user_id")
        self.nickname: str = sender.get("nickname")
        self.card: str = sender.get("card")
        self.role: str = sender.get("role")

        self.message: str = data.get("message")
        self.raw_message: str = data.get("raw_message")
        self.message_id: int = data.get("message_id")
        self.group_id: int = data.get("group_id")
        ...

    def post_event(self, debug):
        log.debug(
            f"收到来自群聊 {self.group_id} 的消息：{self.nickname}(群名片：{self.card}，QQ号：{self.user_id})说：{self.message}",
            debug
        )
