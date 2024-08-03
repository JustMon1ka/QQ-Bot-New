from Event.EventHandler.NoticeEventHandler import GroupRecallEvent
from Logging.PrintLog import Log
from Plugins import Plugins
from CQMessage.CQType import At
from Interface.Api import Api
log = Log()


class RecallPrevent(Plugins):
    """
    插件名：RecallPrevent \n
    插件类型：群聊撤回插件 \n
    插件功能：当有人通过私在群聊撤回消息时，bot会自动发送撤回消息内容的消息 \n
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "RecallPrevent"
        self.type = "GroupRecall"
        self.author = "kiriko"
        self.introduction = """
                                插件描述：撤回你的撤回
                                插件功能：自动发送撤回消息内容的消息
                            """
        self.init_status()
        self.latest_message = ""

    async def main(self, event: GroupRecallEvent, debug):

        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")
        group_id = event.group_id
        user_id = event.user_id
        operator_id = event.operator_id
        effected_group_id: list = self.config.get("effected_group")
        message_id = event.message_id
        response = await self.api.OtherAPI.get_msg(self, message_id=event.message_id)
        latest_message = response['data']['message']
        if group_id not in effected_group_id:
            return
        elif user_id == operator_id:  # 正式进入插件运行部分
            reply_message = f"{At(qq=user_id)} 撤回的消息是：{latest_message}"
            try:
                await self.api.groupService.send_group_msg(group_id=group_id, message=reply_message)
            except Exception as e:
                log.error(f"插件：{self.name}运行时出错：{e}")
            else:
                log.debug(f"插件：{self.name}运行正确，成功向{group_id}发送了一条消息：{reply_message}", debug)
        return
