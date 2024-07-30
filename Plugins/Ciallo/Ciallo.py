from CQMessage.CQType import Record
from Plugins import Plugins


class Ciallo(Plugins):
    """
    这是一个插件的模板，开发一个新的插件至少应该包含以下部分
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "Ciallo"
        self.type = "Group"
        self.author = "just monika"
        self.introduction = """
                                柚子厨蒸鹅心
                            """
        self.init_status()

    async def main(self, event, debug):

        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")

        message: str = event.message
        command_list = message.split(" ")
        len_of_command = len(command_list)
        if command_list[0] != self.bot.bot_name:
            return
        if len_of_command < 2:
            return

        command = self.config.get("command")
        if command_list[1] != command:
            return
        else:  # 正式进入插件运行部分
            group_id = event.group_id
            effected_group: list = self.config.get("effected_group")
            if group_id not in effected_group:
                await self.api.groupService.send_group_msg(group_id=group_id, message=f"该功能未在此群{group_id}生效")
                return
            else:
                audio_url = self.config.get("audio_url")
                await self.api.groupService.send_group_msg(group_id=group_id, message=f"{Record(file=audio_url)}")
        return
