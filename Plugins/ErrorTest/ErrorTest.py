from Plugins import Plugins
from Logging.PrintLog import Log
from Event.EventHandler.PrivateMessageEventHandler import PrivateMessageEvent
log = Log()


class ErrorTest(Plugins):
    """
    插件名：ErrorTest \n
    插件类型：私聊插件 \n
    插件功能： 当通过私聊向bot发送"error"时，将此插件的运行状态设置为error\n
    这是一个测试插件，没有实际意义
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "ErrorTest"
        self.type = "Group"
        self.author = "just monika"
        self.introduction = """
                                这是一个测试插件，没有实际意义
                                插件功能：当通过私聊向bot发送"error"时，将此插件的运行状态设置为error
                            """
        self.init_status()

    def main(self, event: PrivateMessageEvent, debug, config):
        enable = eval(config.get("enable"))
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")
        message = event.message
        if message == "error":
            self.set_status("error")
            log.debug("成功将该插件状态变为error", debug)
            self.api.privateService.send_private_msg("成功将该插件状态变为error")
