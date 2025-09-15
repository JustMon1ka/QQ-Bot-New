from Event.EventHandler.NoticeEventHandler import GroupPokeEvent
from Logging.PrintLog import Log
from Plugins import Plugins
from CQMessage.CQType import At, Face
from random import randint

log = Log()


class DontPoke(Plugins):
    """
    插件名：DontPoke \n
    插件类型：群聊戳一戳插件 \n
    插件功能：当有人戳一戳时，bot作出回复（PokeHandler测试） \n
    """

    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "DontPoke"
        self.type = "Poke"
        self.author = "Heai"
        self.introduction = """
                                插件描述：戳什么戳！
                                插件功能：回复戳一戳
                            """
        self.init_status()

    async def main(self, event: GroupPokeEvent, debug):
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
        
        target_id = event.target_id
        self_id = event.self_id
        if (target_id != self_id):
            return

        user_id = event.user_id

        if user_id == 2046889405:
            message = f"{At(qq=user_id)} {Face(id=319)}"
        else:
            message_list = [
                "戳什么戳！",
                "喵喵喵",
                "叔叔你别戳了我害怕",
                f"滚{Face(id=326)}",
                "你没活可以咬打火机",
                "呜——",
                "还戳，再戳ban你喵",
                "扑棱我干哈？",
                "把你种进土里，你重新长吧",
                "哼~",
                "哎呦疼——"
            ]
            message = f"{At(qq=user_id)} " + message_list[randint(0, len(message_list) - 1)]
        self.api.groupService.send_group_msg(group_id=group_id, message=message)

        return