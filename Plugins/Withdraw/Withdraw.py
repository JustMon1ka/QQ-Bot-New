from CQMessage.CQType import At, Reply
from Event.EventHandler import GroupMessageEventHandler
from Logging.PrintLog import Log
from Plugins import Plugins

log = Log()

class Withdraw(Plugins):
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "Withdraw"
        self.type = "Group"
        self.author = "Beholder123"
        self.introduction = """
                                        助教可使用机器人进行消息撤回处理
                            """
        self.init_status()

    async def main(self, event: GroupMessageEventHandler, debug):

        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")

        message: str = event.message
        j = 0
        true_message = ""
        for i in range(0, len(message)):
            if message[i] == ']':
                j = i+1
                break
        for i in range(j, len(message)):
            true_message += message[i]
        command_list = true_message.split(" ")
        command = self.config.get("command")
        if command_list[1] != command:
            return
        else:
            group_id = event.group_id
            effected_group: list = self.config.get("effected_group")
            if group_id not in effected_group:
                self.api.groupService.send_group_msg(group_id=group_id, message=f"该功能未在此群{group_id}生效")
                return
            else:
                user_id = event.user_id
                sender_card = event.card.split("-")
                if len(sender_card) != 3:
                    self.api.groupService.send_group_msg(group_id=group_id,
                                                         message=f"{At(qq=user_id)} 群名片格式不正确，请改正后再进行查询")
                    return
                else:
                    if sender_card[1] == "助教":
                        target_message_id = ""
                        if message[0:13] == "[CQ:reply,id=":
                            for i in range(13, len(message)):
                                if message[i]==']':
                                    break
                                target_message_id += message[i]
                            try:
                                self.api.groupService.delete_msg(message_id=target_message_id)
                            except Exception as e:
                                log.error(f"插件：{self.name}运行时出错：{e}")
                            else:
                                log.debug(f"插件：{self.name}运行正确，成功在{group_id}中撤回了一条消息：{event.message}", debug)
