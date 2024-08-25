from Event.EventHandler.GroupMessageEventHandler import GroupMessageEvent
from Logging.PrintLog import Log
from Plugins import Plugins
log = Log()


class Repeater(Plugins):
    """
    插件名：repeater \n
    插件类型：私聊插件 \n
    插件功能：当群聊有一定数量条复读消息时，bot会撤回最后一个复读消息并禁言该用户十分钟 \n
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "Repeater"
        self.type = "Group"
        self.author = "kiriko"
        self.introduction = """
                                插件描述：人类的本质……
                                插件功能：当群聊有一定数量条复读消息时，bot会撤回最后一个复读消息并禁言该用户十分钟
                            """
        self.init_status()
        self.message_latest: str = ""
        self.counts = 0
        
    async def main(self, event: GroupMessageEvent, debug):
        
        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")
        group_id = event.group_id
        effected_group: list = self.config.get("effected_group")
        threshold = int(self.config.get("threshold"))
        ban = bool(self.config.get("ban"))
        recall = bool(self.config.get("recall"))
        for_everyone = bool(self.config.get("for_everyone"))
        if group_id not in effected_group:
            return
        
        message_newest = event.message
        if message_newest != self.message_latest:
            self.message_latest = message_newest
            self.counts = 1
        else:
            self.counts += 1
             
        #到达阈值时正式进行插件的运行
        if self.counts >= threshold:
            reply_message = self.config.get("normal_message")
            card_cuts = event.card.split("-")
            ban_time = self.config.get("ban_time")
            ban_time_cuts = ban_time.split(":")
            duration = int(ban_time_cuts[0])*3600 + int(ban_time_cuts[1])*60 + int(ban_time_cuts[0])
            if len(card_cuts) == 3:
                if card_cuts[1] == "助教":
                    if for_everyone:
                        reply_message = self.config.get("special_message")
                    else:
                        return
            if recall:
                try:
                    self.api.groupService.delete_msg(message_id=event.message_id)
                except Exception as e:
                    log.error(f"插件：{self.name}运行时出错：{e}")
                else:
                    log.debug(f"插件：{self.name}运行正确，成功在{group_id}中撤回了一条消息：{event.message}", debug)
            if ban:
                try:
                    self.api.groupService.set_group_ban(group_id=group_id, user_id=event.user_id,
                                                          duration=duration)
                except Exception as e:
                    log.error(f"插件：{self.name}运行时出错：{e}")
                else:
                    log.debug(f"插件：{self.name}运行正确，成功将用户{event.user_id}禁言{ban_time}", debug)
            try:
                self.api.groupService.send_group_msg(group_id=group_id, message=reply_message)
            except Exception as e:
                log.error(f"插件：{self.name}运行时出错：{e}")
            else:
                log.debug(f"插件：{self.name}运行正确，成功向{group_id}发送了一条消息：{reply_message}", debug)
        return
