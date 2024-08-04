import re
from Event.EventHandler.RequestEventHandler import GroupRequestEvent
from sqlalchemy import Column, Integer, String, select, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from Logging.PrintLog import Log
from Plugins import Plugins
from Interface.Api import Api

log = Log()


class GroupApprove(Plugins):
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "GroupApprove"  # 插件的名字（一定要和类的名字完全一致（主要是我能力有限，否则会报错））
        self.type = "GroupRequest"  # 插件的类型（这个插件是在哪种消息类型中触发的）
        self.author = "kiriko"  # 插件开发作者（不用留真名，但是当插件报错的时候需要根据这个名字找到对应的人来修）
        self.introduction = """
                                自动处理入群申请,当回答入群答案和设置内的good_request相同是自动同意申请
                            """
        self.init_status()
        self.real_answer = ""
        self.all_inform = None
        self.spacer = ""

    async def main(self, event: GroupRequestEvent, debug):
        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")

        if self.all_inform is None:
            while True:
                try:
                    self.all_inform = await self.select_all_infom()
                    log.debug("初始化验证信息成功", debug)
                    break
                except Exception as e:
                    log.debug(e, debug=debug)
                    continue

        group_id = event.group_id
        effected_group: list = self.config.get('effected_group')
        if group_id not in effected_group:
            return
        else:

            self.spacer = self.config.get("spacer")
            if not self.spacer:
                self.spacer = " "
            sub_type = event.sub_type
            if sub_type != "add":
                return
            # 正式进入插件运行部分
            flag = event.flag
            full_comment = event.comment
            requests = full_comment.split('\n答案：')
            self.real_answer = requests[1]
            reject_flag = self.config.get("reject")
            if not self.request_conform(debug):
                if reject_flag:
                    reasons = self.config.get("reason")
                    reason = reasons[0] + self.spacer + reasons[1]
                    try:
                        await self.api.GroupService.set_group_add_request(self, flag=flag, approve="false",
                                                                          reason=reason)
                    except Exception as e:
                        log.error(f"插件：{self.name}运行时出错：{e}")
                    else:
                        log.debug(f"插件：{self.name}运行正确，成功将{group_id}中的正确入群申请{flag}拒绝，"
                                  f"拒绝理由为{reason}", debug)
            else:
                answer_cuts = self.real_answer.split(self.spacer)
                stu_id = int(answer_cuts[0])
                if self.stu_id_conform(stu_id):
                    try:
                        await self.api.GroupService.set_group_add_request(self, flag=flag)
                    except Exception as e:
                        log.error(f"插件：{self.name}运行时出错：{e}")
                    else:
                        log.debug(f"插件：{self.name}运行正确，成功将{group_id}中的正确入群申请{flag}批准", debug)
                else:
                    log.debug(f"插件：{self.name}运行正确，成功将{group_id}中的未查询到学号信息的入群申请{flag}挂起", debug)


    def request_conform(self, debug):
        answer_cuts = self.real_answer.split(self.spacer)
        parts = self.config.get("parts")
        if len(answer_cuts) != int(parts):
            return False
        if not answer_cuts[0].isdigit():
            return False
        return True

    def stu_id_conform(self, stu_id):
        try:
            data = self.all_inform.get("data")
            select_result = data.get(stu_id)
        except Exception as e:
            raise e
        if select_result:
            return True

    async def select_all_infom(self):
        async_sessions = sessionmaker(
            bind=self.bot.database,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with async_sessions() as sessions:
            raw_table = select(self.StuInformation)
            results = await sessions.execute(raw_table)

            indexs = results.scalars().all()
            indexs_dict = {lc.stu_id: {'name': lc.name, 'major_short': lc.major_short, 'ingroup': lc.ingroup} for lc in
                           indexs}

            return {'data': indexs_dict}

    Basement = declarative_base()

    class StuInformation(Basement):
        __tablename__ = 'stu_imformation'
        stu_id = Column(Integer, primary_key=True)
        name = Column(String)
        major_short = Column(String)
        ingroup = Column(Integer)
