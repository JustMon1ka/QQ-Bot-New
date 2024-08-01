from CQMessage.CQType import At 
from Plugins import Plugins


class Goujiao(Plugins):
    """
    这是一个插件的模板，开发一个新的插件至少应该包含以下部分
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "Goujiao"  # 插件的名字（一定要和类的名字完全一致（主要是我能力有限，否则会报错））
        self.type = "Group"  # 插件的类型（这个插件是在哪种消息类型中触发的）
        self.author = "budenghao"  # 插件开发作者（不用留真名，但是当插件报错的时候需要根据这个名字找到对应的人来修）
        self.introduction = """
                                对狗叫的人禁言
                                目前只支持特定人
                            """
        self.init_status()

    async def main(self, event, debug):
        """
        函数的入口，每个插件都必须有一个主入口 \n
        受到框架限制，所有插件的main函数的参数必须是这几个，不能多也不能少 \n
        注意！所有的插件都需要写成异步的方法，防止某个插件出问题卡死时导致整个程序阻塞
        :param event: 消息事件体
        :param debug: 是否输出debug信息
        :param config: 配置文件对象
        :return:
        """
        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")

        botname = self.config.get("botname")
        message: str = event.message
        command_list = message.split(" ")
        len_of_command = len(command_list)
        if botname:
            if command_list[0] != self.bot.bot_name:
                return
            if len_of_command < 2:
                return
        
        command = self.config.get("command")
        #botname/no botname
        if botname:
            if command_list[1] != command:
                return
        elif    command_list[0] != command:
            return
        else:
            group_id = event.group_id
            effected_group: list = self.config.get("effected_group")
            all_reply_message : list = self.config.get("goujiao")
            ban_id = self.config.get("ban_id")
            joined_string = "\n".join(all_reply_message)
            if group_id not in effected_group:
                await self.api.groupService.send_group_msg(group_id=group_id, message=f"该功能未在此群{group_id}生效")
                return
            else:
                #await self.api.groupService.send_group_msg(group_id=group_id,message=f"{At(qq=ban_id)}"+joined_string)
                await self.api.groupService.send_group_msg(group_id=group_id, message=joined_string)
                await self.api.groupService.mute_group_member(group_id=group_id,user_id=ban_id,duration=60)
        return
