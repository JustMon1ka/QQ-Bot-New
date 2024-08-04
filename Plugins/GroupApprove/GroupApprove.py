from Event.EventHandler.RequestEventHandler import GroupRequestEvent
from Logging.PrintLog import Log
from Plugins import Plugins
from Interface.Api import Api

log = Log()


class GroupApprove(Plugins):
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "GroupApprove"  # 插件的名字（一定要和类的名字完全一致（主要是我能力有限，否则会报错））
        self.type = "GroupRequest"  # 插件的类型（这个插件是在哪种消息类型中触发的）
        self.author = "just monika"  # 插件开发作者（不用留真名，但是当插件报错的时候需要根据这个名字找到对应的人来修）
        self.introduction = """
                                自动处理入群申请,当回答入群答案和设置内的good_request相同是自动同意申请
                            """
        self.init_status()
        self.real_answer = ""

    async def main(self, event: GroupRequestEvent, debug):
        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")

        group_id = event.group_id
        effected_group: list = self.config.get('effected_group')
        if group_id not in effected_group:
            return
        else:
            sub_type = event.sub_type
            if sub_type != "add":
                return
            # 正式进入插件运行部分
            flag = event.flag
            full_comment = event.comment
            requests = full_comment.split('\n答案：')
            self.real_answer = requests[1]
            if self.request_config():
                try:
                    await self.api.GroupService.set_group_add_request(self, flag=flag)
                except Exception as e:
                    log.error(f"插件：{self.name}运行时出错：{e}")
                else:
                    log.debug(f"插件：{self.name}运行正确，成功将{group_id}中的正确入群申请{flag}批准", debug)

    def request_config(self):

        return True
