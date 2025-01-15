from Event.EventHandler.NoticeEventHandler import GroupRecallEvent
from Logging.PrintLog import Log
from Plugins import Plugins
from CQMessage.CQType import At
from Interface.Api import Api
import redis
import random
import json

log = Log()


class RecallPrevent(Plugins):
    """
    插件名：RecallPrevent \n
    插件类型：群聊撤回插件 \n
    插件功能：当有人通过私在群聊撤回消息时，bot会自动发送撤回消息内容的消息 \n
    """

    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "RecallPrevent"
        self.type = "GroupRecall"
        self.author = "kiriko"
        self.introduction = """
                                插件描述：撤回你的撤回
                                插件功能：自动发送撤回消息内容的消息
                            """
        self.redis_client = None
        self.init_status()

    async def main(self, event, debug):
        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")

        # 初始化同步 Redis 连接
        if not self.redis_client:
            host = self.config.get("host", "localhost")
            port = int(self.config.get("port", 6379))
            db = int(self.config.get("db", 0))
            self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

        group_id = event.group_id
        effected_group_id: list = self.config.get("effected_group")
        if group_id not in effected_group_id:
            return

        if event.post_type == "message":  # 当获取消息时将消息的信息存入redis
            # 获取消息和消息ID
            message = event.message
            sender = event.card
            data = {
                "message": message,
                "card": sender
            }

            message_id = event.message_id

            try:
                json_data = json.dumps(data)
                self.redis_client.setex(f"message:{message_id}", 180, json_data)
                log.debug(f"已成功存储消息 ID: {message_id}，消息内容：{event}", debug)
            except Exception as e:
                log.error(f"插件：{self.name} 存储消息到 Redis 时出错：{e}")

            return

        user_id = event.user_id
        operator_id = event.operator_id

        # 获取消息数据
        response = self.get_message(event.message_id)
        if not response:
            log.error(f"未能找到消息 ID: {event.message_id}，请确认消息已存储.")
            return

        try:
            response_data = json.loads(response)
            card_cuts = response_data['card'].split("-")
            recalled_message = response_data['message']
        except Exception as e:
            log.error(f"解析 Redis 数据时出错：{e}")
            return

        for_everyone = bool(self.config.get("for_everyone"))
        ban = bool(self.config.get("ban"))
        ban_time = self.config.get("ban_time")
        ban_time_cuts = ban_time.split("-")
        min_ban_time = ban_time_cuts[0].split(":")
        max_ban_time = ban_time_cuts[1].split(":")
        ignored_ids: list = self.config.get("ignored_ids")
        duration = random.randint(int(min_ban_time[0]) * 3600 + int(min_ban_time[1]) * 60 +
                                  int(min_ban_time[2]), int(max_ban_time[0]) * 3600 + int(max_ban_time[1]) * 60 +
                                  int(max_ban_time[2]))

        if len(card_cuts) == 3:
            if card_cuts[1] == "助教":
                if not for_everyone:
                    return
        if event.user_id in ignored_ids:
            return
        if user_id == operator_id:  # 正式进入插件运行部分
            reply_message = f"{At(qq=user_id)} 撤回的消息是：{recalled_message}"
            try:
                self.api.groupService.send_group_msg(group_id=group_id, message=reply_message)
            except Exception as e:
                log.error(f"插件：{self.name}运行时出错：{e}")
            else:
                log.debug(f"插件：{self.name}运行正确，成功向{group_id}发送了一条消息：{reply_message}", debug)

            if ban:
                try:
                    self.api.groupService.set_group_ban(group_id=group_id, user_id=event.user_id, duration=duration)
                except Exception as e:
                    log.error(f"插件：{self.name}运行时出错：{e}")
                else:
                    log.debug(f"插件：{self.name}运行正确，成功将用户{event.user_id}禁言{duration}秒", debug)
        return

    def get_message(self, message_id):
        return self.redis_client.get(f"message:{message_id}")
