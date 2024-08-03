from Logging.PrintLog import Log

log = Log()


class GroupRecallEvent:

    def __init__(self, data):
        self.time: int = data.get("time")
        self.self_id: int = data.get("self_id")
        self.post_type: str = data.get("post_type")
        self.notice_type: str = data.get("notice_type")
        self.group_id: int = data.get("group_id")
        self.user_id: int = data.get("user_id")
        self.operator_id: int = data.get("operator_id")
        self.message_id: int = data.get("message_id")
        ...

    def post_event(self, debug):
        log.debug(
            f"在群 {self.group_id} 中，消息 ID {self.message_id} 被撤回。"
            f"发送者：{self.user_id}，操作者：{self.operator_id}，事件发生时间：{self.time}",
            debug
            )
