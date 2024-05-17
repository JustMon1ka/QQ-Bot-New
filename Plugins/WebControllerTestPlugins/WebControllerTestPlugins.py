from Logging.PrintLog import Log
from Plugins import Plugins
log = Log()


class WebControllerTestPlugins(Plugins):
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "WebControllerTestPlugins"
        self.type = "Private"
        self.author = "just monika"
        self.introduction = """
                                这个插件是用来测试web控制面板的日志输出功能的，没有实际意义
                            """
        self.init_status()

    async def main(self, event, debug):
        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")
        message = event.message
        if message == "tset":
            for _ in range(15):
                log.debug("Debug Test", True)
            user_id = event.user_id
            await self.api.privateService.send_private_msg(user_id, "成功生成了一些随机日志")
