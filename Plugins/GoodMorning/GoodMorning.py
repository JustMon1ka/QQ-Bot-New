import requests

from CQMessage.CQType import At
from Event.EventHandler import GroupMessageEventHandler
from Logging.PrintLog import Log
from Plugins import Plugins
from sqlalchemy import Column, Integer, DATETIME, select, BigInteger, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update, delete
from datetime import datetime, timedelta, time

log = Log()

class GoodMorning(Plugins):
    """
    这是一个插件的模板，开发一个新的插件至少应该包含以下部分
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "GoodMorning"  # 插件的名字（一定要和类的名字完全一致（主要是我能力有限，否则会报错））
        self.type = "Group"  # 插件的类型（这个插件是在哪种消息类型中触发的）
        self.author = "just monika"  # 插件开发作者（不用留真名，但是当插件报错的时候需要根据这个名字找到对应的人来修）
        self.introduction = """
                                早安/晚安插件
                            """
        self.init_status()

    async def main(self, event: GroupMessageEventHandler, debug):
        """
        函数的入口，每个插件都必须有一个主入口 \n
        受到框架限制，所有插件的main函数的参数必须是这几个，不能多也不能少 \n
        注意！所有的插件都需要写成异步的方法，防止某个插件出问题卡死时导致整个程序阻塞
        :param event: 消息事件体
        :param debug: 是否输出debug信息
        :return:
        """
        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")

        message = event.message
        command = message.split(" ")
        if len(command) != 2:
            return
        if command[0] != self.bot.bot_name:
            return

        if event.group_id not in self.config.get("effected_groups"):
            return

        if command[1] == self.config.get("good_morning"):
            morning_time = datetime.strptime(self.config.get("morning_time"), "%H:%M:%S").time()
            current_time = datetime.now().time()

            if current_time < morning_time:
                self.api.groupService.send_group_msg(group_id=event.group_id, message=f"还没有到{morning_time}哦，再睡一会儿吧！")
            else:
                result = self.good_morning_sign_in(event.user_id)
                if result.get("result"):
                    rank = result.get("rank")
                    if current_time < datetime.strptime("11:00:00", "%H:%M:%S").time():
                        self.api.groupService.send_group_msg(group_id=event.group_id, message=f"早上好呀! {At(qq=event.user_id)} 今天你是本群第{rank}个早安的")
                    elif current_time < datetime.strptime("13:00:00", "%H:%M:%S").time():
                        self.api.groupService.send_group_msg(group_id=event.group_id, message=f"{At(qq=event.user_id)} 都中午了才起床嘛，难道是被饿醒的？今天你是本群第{rank}个早安的")
                    elif current_time < datetime.strptime("18:00:00", "%H:%M:%S").time():
                        self.api.groupService.send_group_msg(group_id=event.group_id, message=f"竟然下午才起床？是不是昨晚又熬夜啦？{At(qq=event.user_id)} 今天你是本群第{rank}个早安的")
                    else:
                        self.api.groupService.send_group_msg(group_id=event.group_id, message=f'{At(qq=event.user_id)} 早在哪里？今天你是本群第{rank}个"早安"的')
                else:
                    self.api.groupService.send_group_msg(group_id=event.group_id, message=f"今天你已经早安过了哦，明天再来吧！{At(qq=event.user_id)}")

        if command[1] == self.config.get("good_night"):
            current_time = datetime.now().time()
            if current_time < datetime.strptime("06:00:00", "%H:%M:%S").time():
                self.api.groupService.send_group_msg(group_id=event.group_id, message=f"{At(qq=event.user_id)} 晚安！下次记得早点睡哦。祝你有个好梦(。-ω-)zzz")
            elif current_time < datetime.strptime("11:00:00", "%H:%M:%S").time():
                self.api.groupService.send_group_msg(group_id=event.group_id, message=f"{At(qq=event.user_id)} 小懒虫刚起床就要晚安？那只好满足你了(^_−)☆")
            elif current_time < datetime.strptime("13:00:00", "%H:%M:%S").time():
                self.api.groupService.send_group_msg(group_id=event.group_id, message=f"{At(qq=event.user_id)} 吃完就睡，那很有生活了(●—●)")
            elif current_time < datetime.strptime("18:00:00", "%H:%M:%S").time():
                self.api.groupService.send_group_msg(group_id=event.group_id, message=f"{At(qq=event.user_id)} 这么早就要晚安了吗？是故意的还是不小心的？(*•ω•)")
            else:
                self.api.groupService.send_group_msg(group_id=event.group_id, message=f"{At(qq=event.user_id)} 晚安啦！早睡早起身体好！d=====(￣▽￣*)b")

            if self.config.get("ban"):
                self.api.groupService.set_group_ban(group_id=event.group_id, user_id=event.user_id, duration=self.get_seconds_to_next_6am())

        return

    @classmethod
    def get_seconds_to_next_6am(cls):
        # 如果未提供当前时间，则使用当前系统时间
        current_time = datetime.now()
        current_time_only = current_time.time()  # 获取时间部分

        # 创建时间对象：午夜 00:00:00 和早上 06:00:00
        midnight = time(0, 0, 0)
        six_am = time(6, 0, 0)

        today = current_time.date()  # 获取当前日期

        # 判断当前时间是否在 0:00 AM 到 6:00 AM 之间
        if midnight <= current_time_only < six_am:
            target_6am = datetime.combine(today, six_am)
        else:
            next_day = today + timedelta(days=1)
            target_6am = datetime.combine(next_day, six_am)

        # 返回当前时间到目标 6:00 AM 的秒数差
        return int((target_6am - current_time).total_seconds())

    Basement = declarative_base()

    class GoodMorningDB(Basement):
        __tablename__ = "good_morning"
        user_id = Column(BigInteger, primary_key=True)
        morning_time = Column(DATETIME)
        rank = Column(Integer)
        counts = Column(Integer)

    def good_morning_sign_in(self, user_id: int):
        """
        处理用户的签到操作。

        参数:
            user_id (int): 用户ID

        返回:
            dict: 包含 morning_time 和 rank 的字典
        """
        params = {
            "user_id": user_id,
        }
        return requests.get(self.config.get("morning_api"), params=params).json()
