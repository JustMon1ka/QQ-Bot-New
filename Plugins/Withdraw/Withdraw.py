
from CQMessage.CQType import At
import random
import re
from CQMessage.CQHelper import CQHelper
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


        full_message: str = event.message
        pattern = re.compile(r'(\[CQ:reply,id=.+\])(.+)')
        p = pattern.match(full_message)
        if p is None:
            return
        message = p.group(2)
        command_list = message.split(" ")
        command = self.config.get("command")
        len_of_command = len(command_list)
        if command_list[0] != self.bot.bot_name:
            return
        if len_of_command < 2:
            return

        if command_list[1] != command:
            return
        else:
            group_id = event.group_id
            effected_group: list = self.config.get("effected_group")
            if group_id not in effected_group:
                self.api.groupService.send_group_msg(group_id=group_id, message=f"该功能未在此群{group_id}生效")
                return

            else:  #插件正式执行
                user_id = event.user_id
                assistants_list = self.handle_raw_list(self.get_assistant_raw_list())
                operator_list = event.card.split("-")
                if len(operator_list) == 3:
                    operator_role = operator_list[1]
                    if operator_role != "助教" and operator_role != "围观":
                        self.api.groupService.send_group_msg(group_id=group_id, message="只有助教可以使用此功能")
                        return
                    else:
                        if self.is_assistant(user_id, assistants_list):
                            pass
                        else:
                            self.api.groupService.send_group_msg(group_id=group_id, message="big胆，敢冒充助教")
                            ban = self.config.get("ban")
                            if ban:
                                min_ban_time = self.config.get("Min")
                                max_ban_time = self.config.get("Max")
                                duration = random.randint(min_ban_time, max_ban_time)
                                self.api.groupService.set_group_ban(group_id=group_id, user_id=event.user_id,
                                                                    duration=duration)
                            return
                else:
                    if event.user_id == 278787983:  # 这个是渣哥的QQ号
                        pass
                    else:
                        self.api.groupService.send_group_msg(group_id=group_id,
                                                             message=f"{At(qq=user_id)}连自己名片都改不对还想撤回消息？")
                        return
                obj = CQHelper.load_cq(full_message)
                target_message_id = obj.reply
                try:
                    self.api.groupService.delete_msg(message_id=target_message_id)
                    recall_command = self.config.get("recall_command")
                    if recall_command:
                        self.api.groupService.delete_msg(message_id=event.message_id)
                except Exception as e:
                    log.error(f"插件：{self.name}由{event.user_id}发起，但运行时出错：{e}")
                else:
                    log.debug(f"插件：{self.name}由{event.user_id}发起，运行正确，，成功在{group_id}中撤回了一条消息：{event.message}", debug)

    @classmethod
    def is_assistant(cls, user_id, assistant_list):
        return user_id in assistant_list


    def get_assistant_raw_list(self):
        group_id = self.config.get("assistants_group")
        return self.api.groupService.get_group_member_list(group_id=group_id).get("data")

    @classmethod
    def handle_raw_list(cls, raw_list):
        assistants_user_id_list = []
        for info in raw_list:
            user_id = info.get("user_id")
            assistants_user_id_list.append(user_id)
        return assistants_user_id_list

