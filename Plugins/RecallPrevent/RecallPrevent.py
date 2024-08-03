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

    async def main(self, event: GroupRecallEvent, debug):

        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")
        group_id = event.group_id
        effected_group_id: list = self.config.get("effected_group")
        if group_id not in effected_group_id:
            return
        user_id = event.user_id
        operator_id = event.operator_id
        response = await self.api.MessageService.get_msg(self, message_id=event.message_id)
        card_cuts = response['data']['sender']['card'].split("-")
        recalled_message = response['data']['message']
        for_everyone = bool(self.config.get("for_everyone"))
        ban = bool(self.config.get("ban"))
        ban_time = self.config.get("ban_time")
        ban_time_cuts = ban_time.split(":")
        duration = int(ban_time_cuts[0]) * 3600 + int(ban_time_cuts[1]) * 60 + int(ban_time_cuts[0])
        if len(card_cuts) == 3:
            if card_cuts[1] == "助教":
                if not for_everyone:
                    return
        if user_id == operator_id:  # 正式进入插件运行部分
            reply_message = f"{At(qq=user_id)} 撤回的消息是：{recalled_message}"
            try:
                await self.api.groupService.send_group_msg(group_id=group_id, message=reply_message)
            except Exception as e:
                log.error(f"插件：{self.name}运行时出错：{e}")
            else:
                log.debug(f"插件：{self.name}运行正确，成功向{group_id}发送了一条消息：{reply_message}", debug)
            if ban:
                try:
                    await self.api.groupService.set_group_ban(group_id=group_id, user_id=event.user_id,
                                                              duration=duration)
                except Exception as e:
                    log.error(f"插件：{self.name}运行时出错：{e}")
                else:
                    log.debug(f"插件：{self.name}运行正确，成功将用户{event.user_id}禁言{ban_time}", debug)
        return
