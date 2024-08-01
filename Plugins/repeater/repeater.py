from Event.EventHandler.PrivateMessageEventHandler import PrivateMessageEvent
from Logging.PrintLog import Log
from Plugins import Plugins
log = Log()

message_latest: str = ""
counts=0

class repeater(Plugins):
    """
    插件名：repeater \n
    插件类型：私聊插件 \n
    插件功能：当群聊有一定数量条复读消息时，bot会撤回最后一个复读消息并禁言该用户十分钟 \n
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = " repeater"
        self.type = "Group"
        self.author = "kiriko"
        self.introduction = """
                                插件描述：人类的本质……
                                插件功能：当群聊有一定数量条复读消息时，bot会撤回最后一个复读消息并禁言该用户十分钟
                            """
        self.init_status()

    async def main(self, event: PrivateMessageEvent, debug):
        global message_latest
        global counts
        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")
        group_id = event.group_id
        effected_group: list = self.config.get("effected_group")
        threshold = int(self.config.get("threshold"))
        if group_id not in effected_group:
            return
        else:
            while(1):  
              message_newest = event.message  
              if message_newest !=message_latest:
                  message_latest= message_newest
                  counts=0
              else:
                 counts += 1
                 #到达阈值时正式进行插件的运行
                 if counts == threshold:
                      reply_message = "请不要复读"
                      counts = 0
                      try:
                         await self.api.groupService.delete_msg(message_id=event.message_id)
                         await self.api.groupService.send_group_msg(group_id=group_id, message=reply_message)
                         await self.api.groupService.set_group_ban(group_id=group_id, user_id=event.user_id,duration=10*60)
                      except Exception as e:
                        log.error(f"插件：{self.name}运行时出错：{e}")
                      else:
                        log.debug(f"插件：{self.name}运行正确，成功在{group_id}中撤回了一条消息：{event.message}", debug)
                        log.debug(f"插件：{self.name}运行正确，成功向{group_id}发送了一条消息：{reply_message}", debug)
                        log.debug(f"插件：{self.name}运行正确，成功将用户{event.user_id}禁言10分钟", debug)
                 return
