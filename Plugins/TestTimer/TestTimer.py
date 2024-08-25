import asyncio
import threading

from Event.EventHandler.GroupMessageEventHandler import GroupMessageEvent
from Plugins import Plugins


class TestTimer(Plugins):
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "TestTimer"  # 插件的名字（一定要和类的名字完全一致（主要是我能力有限，否则会报错））
        self.type = "Group"  # 插件的类型（这个插件是在哪种消息类型中触发的）
        self.author = "somebody"  # 插件开发作者（不用留真名，但是当插件报错的时候需要根据这个名字找到对应的人来修）
        self.introduction = """
                                这是一个插件的模板，开发一个新的插件至少应该包含以下部分
                            """
        self.init_status()

        self.timer = None
        self.timer_lock = threading.Lock()

    async def main(self, event: GroupMessageEvent, debug):
        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")

        repeat_message = self.config.get("repeat_message")
        repeat_seconds = int(self.config.get("repeat_seconds"))
        start_signal = self.config.get("start_signal")
        stop_signal = self.config.get("stop_signal")

        message = event.message
        group_id = event.group_id

        if message == stop_signal:
            self.stop_timer(stop_signal, message, group_id)
        elif message == start_signal:
            self.start_timer(repeat_seconds, repeat_message, group_id)

    def start_timer(self, repeat_seconds, repeat_message, group_id):
        # 确保线程安全，防止多个线程同时访问 timer
        with self.timer_lock:
            if self.timer is None:
                self.api.groupService.send_group_msg(group_id=group_id, message="Starting timer...")
                self.timer = threading.Timer(repeat_seconds, self.timer_action, args=(repeat_seconds, repeat_message, group_id))
                self.timer.start()
            else:
                self.api.groupService.send_group_msg(group_id=group_id, message="Timer already running.")

    def timer_action(self, repeat_seconds, repeat_message, group_id):
        with self.timer_lock:
            if self.timer is not None:
                self.api.groupService.send_group_msg(group_id=group_id, message=repeat_message)
                # 重新启动计时器
                self.timer = threading.Timer(repeat_seconds, self.timer_action, args=(repeat_seconds, repeat_message, group_id))
                self.timer.start()

    def stop_timer(self, stop_signal, message, group_id):
        if message == stop_signal:
            with self.timer_lock:
                if self.timer is not None:
                    self.api.groupService.send_group_msg(group_id=group_id, message="Stopping timer...")
                    self.timer.cancel()
                    self.timer = None
                else:
                    self.api.groupService.send_group_msg(group_id=group_id, message="No timer to stop.")



