import requests

from Event.EventHandler.GroupMessageEventHandler import GroupMessageEvent
from CQMessage.CQHelper import CQHelper
from CQMessage.CQType import CQMessage
from CQMessage.CQType import At, Reply
from Logging.PrintLog import Log
from Plugins import Plugins
log = Log()


class Screenshot(Plugins):

    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "Screenshot"
        self.type = "Group"
        self.author = "just monika"
        self.introduction = """
                                插件描述：检测图片是否是拍屏
                            """
        self.init_status()

    async def main(self, event: GroupMessageEvent, debug):
        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return
        if self.status != "error":
            self.set_status("running")
        if event.group_id not in self.config.get("effected_group"):
            return

        message = event.message
        image_cq: CQMessage = CQHelper.load_cq(message)

        if not image_cq or image_cq.cq_type != "image":
            return
        image_url = image_cq.url
        if not image_url:
            return

        # 下载文件
        local_file_path = self.config.get("local_file_path")
        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                with open(local_file_path, "wb") as f:
                    f.write(response.content)
            else:
                log.warning(f"图片下载失败，状态码：{response.status_code}")
                return
        except requests.exceptions.RequestException as e:
            log.error(f"图片下载失败：{e}")
            return

        api = self.config.get("api")
        with open(local_file_path, "rb") as f:
            files = {'file': (local_file_path.split("/")[-1], f)}  # 自动提取文件名

            try:
                res = requests.post(api, files=files, timeout=10)

                # 处理响应
                if res.status_code == 200:
                    predict = res.json()
                    log.debug(f"预测结果：{predict}", debug=debug)
                else:
                    log.warning(f"请求失败，状态码：{res.status_code}")
                    log.warning(f"错误信息：{res.text}")

            except requests.exceptions.RequestException as e:
                log.error(f"请求api异常：{e}")

        if predict.get("class") == "cameracap":
            reply = ""
            if self.config.get("at"):
                reply += str(Reply(event.message_id))
                reply += str(At(event.user_id))
            reply += self.config.get("reply")
            if self.config.get("detail"):
                reply += f"\nconfidence: {predict.get('confidence')}"
            self.api.groupService.send_group_msg(message=reply, group_id=event.group_id)


