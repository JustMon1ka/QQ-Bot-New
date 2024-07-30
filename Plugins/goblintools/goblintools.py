
from Event.EventHandler.PrivateMessageEventHandler import PrivateMessageEvent
from Logging.PrintLog import Log
from Plugins import Plugins
import requests
from urllib import parse
log = Log()


class goblintools(Plugins):
    """
    插件名：goblintools \n
    插件类型：群聊插件 \n
    插件功能：当有人通过指令向bot发送goblintools指令时，bot会访问对应api并返回辛辣的话语 \n
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "goblintools"
        self.type = "Group"
        self.author = "kiriko"
        self.introduction = """
                                插件描述：让文字变得辛辣！
                                插件功能：让作者学习网络爬虫
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
            available_conversions:list=self.config.get("conversions")
            if group_id not in effected_group:
                try:
                     await self.api.groupService.send_group_msg(group_id=group_id, message=f"该功能未在此群{group_id}生效")
                except Exception as e:
                       log.error(f"插件：{self.name}运行时出错：{e}")
                else:
                       log.debug(f"插件：{self.name}运行正确，成功向{group_id}发送了一条消息：该功能未在此群{group_id}生效", debug)
                return
            else:
                if len_of_command < 4:
                     reply_message1 ="请在指令后跟随语言类型，如" +"，".join(available_conversions)+",需要变换的文本内容和辛辣度（1-5，若不输入则默认为3）"
                     try: 
                        await self.api.groupService.send_group_msg(group_id=group_id, message=reply_message1)
                     except Exception as e:
                       log.error(f"插件：{self.name}运行时出错：{e}")
                     else:
                       log.debug(f"插件：{self.name}运行正确，成功向{group_id}发送了一条消息：{reply_message1}", debug)
                     return
                if command_list[2] not in available_conversions:
                     reply_message1 ="语言类型非法，请输入" +"或".join(available_conversions)
                     try: 
                        await self.api.groupService.send_group_msg(group_id=group_id, message=reply_message1)
                     except Exception as e:
                       log.error(f"插件：{self.name}运行时出错：{e}")
                     else:
                       log.debug(f"插件：{self.name}运行正确，成功向{group_id}发送了一条消息：{reply_message1}", debug)
                     return
                if len_of_command > 5:
                     reply_message1 ="请在文本中避免使用空格"
                     try: 
                        await self.api.groupService.send_group_msg(group_id=group_id, message=reply_message1)
                     except Exception as e:
                       log.error(f"插件：{self.name}运行时出错：{e}")
                     else:
                       log.debug(f"插件：{self.name}运行正确，成功向{group_id}发送了一条消息：{reply_message1}", debug)
                     return
                url= self.config.get("api")
                sp1cy_level=3
                if len_of_command == 5:
                 if int(command_list[4])>=1 & int(command_list[4])<=5:
                    sp1cy_level=int(command_list[4])
                txt= command_list[3]
                kv = {
                "Content-Type": "application/json",
                'User-Agent': 'Mozilla/5.0'
                }
                payload={"Text":txt,"Conversion":command_list[2],"Spiciness":sp1cy_level}
                response = requests.post(url,json=payload,headers=kv)
                s=response.content
                ss=s.decode('utf-8').replace('\\x','%')
                un=parse.unquote(ss)
                try:
                     await  self.api.groupService.send_group_msg(group_id=group_id, message=un)
                except Exception as e:
                   log.error(f"插件：{self.name}运行时出错：{e}")
                else:
                    log.debug(f"插件：{self.name}运行正确，成功向{group_id}发送了一条消息：{un}", debug)
        return
