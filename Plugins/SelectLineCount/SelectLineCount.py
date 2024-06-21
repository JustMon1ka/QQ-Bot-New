import asyncio

from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from CQMessage.CQType import At
from Event.EventHandler.GroupMessageEventHandler import GroupMessageEvent
from Logging.PrintLog import Log
from Plugins import Plugins

log = Log()


class SelectLineCount(Plugins):
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "SelectLineCount"  # 插件的名字（一定要和类的名字完全一致（主要是我能力有限，否则会报错））
        self.type = "Group"  # 插件的类型（这个插件是在哪种消息类型中触发的）
        self.author = "just monika"  # 插件开发作者（不用留真名，但是当插件报错的时候需要根据这个名字找到对应的人来修）
        self.introduction = """
                                根据学号从数据库中获取自己本学期一共在高程作业网提交了多少行代码
                            """
        self.init_status()
        self.all_line_count = None

    async def main(self, event: GroupMessageEvent, debug):
        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")

        if self.all_line_count is None:
            while True:
                try:
                    self.all_line_count = await self.select_all_info()
                    log.debug("初始化line_count信息成功", debug)
                    break
                except Exception as e:
                    log.debug(e, debug=debug)
                    continue

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
            if group_id not in effected_group:
                await self.api.groupService.send_group_msg(group_id=group_id, message=f"该功能未在此群{group_id}生效")
                return

            user_id = event.user_id
            sender_card = event.card.split("-")
            if len(sender_card) != 3:
                await self.api.groupService.send_group_msg(group_id=group_id,
                                                           message=f"{At(qq=user_id)} 群名片格式不正确，请改正后再进行查询")
                return
            else:
                stu_id = int(sender_card[0])
                select_result = None
                try:
                    select_result = self.query_by_stu_id(stu_id)
                except Exception as e:
                    raise e

                log.debug(f"查询到的信息是：{select_result}", debug)
                if select_result is not None:
                    count = select_result.get("count")
                    rank = select_result.get("rank")
                    total = select_result.get("total")
                    query_user_id = select_result.get("user_id")
                    if int(query_user_id) != user_id:
                        await self.api.groupService.send_group_msg(group_id=group_id,
                                                                   message=f"{At(qq=user_id)} "
                                                                           f"该学号所有者的QQ号{query_user_id}，与你的QQ号{user_id}不匹配，不予查询！")
                        return
                    else:
                        await self.api.groupService.send_group_msg(group_id=group_id,
                                                                   message=f"{At(qq=user_id)} "
                                                                           f"本学期你一共提交了 {count} 行代码，"
                                                                           f"代码量超过了同期课程的{(rank / total) * 100:.0f}%的学生！")
                else:
                    await self.api.groupService.send_group_msg(group_id=group_id,
                                                               message=f"{At(qq=user_id)} 未查询到学号{stu_id}的信息！")

    def query_by_stu_id(self, stu_id):
        data = self.all_line_count.get("data")
        if stu_id not in data:
            return None
        else:
            result = data.get(stu_id)
            result["total"] = self.all_line_count.get("total")
            return result


    Base = declarative_base()

    class LineCount(Base):
        __tablename__ = 'line_count'

        rank = Column(Integer, primary_key=True, autoincrement=True)
        class_id = Column(String(13), nullable=False)
        stu_id = Column(String(7), unique=True, nullable=False)
        count = Column(Integer)
        user_id = Column(Integer, unique=True)

    async def select_all_info(self):
        async_session = sessionmaker(
            bind=self.bot.database,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with async_session() as session:
            # 查询所有记录
            stmt = select(self.LineCount)
            result = await session.execute(stmt)

            # 将结果转换为字典
            line_counts = result.scalars().all()
            line_count_dict = {lc.stu_id: {'rank': lc.rank, 'count': lc.count, 'user_id': lc.user_id} for lc in line_counts}

            # 查询最后一行数据的index值
            last_row = await session.execute(select(self.LineCount).order_by(self.LineCount.rank.desc()).limit(1))
            last_index = last_row.scalars().first().rank if last_row else None

            # 返回包含所有信息的字典以及最后一行数据的index值
            return {'data': line_count_dict, 'total': last_index}

