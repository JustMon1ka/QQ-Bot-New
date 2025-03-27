import re
from sqlalchemy import Column, Integer, String, select, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update, delete
from Event.EventHandler.GroupMessageEventHandler import GroupMessageEvent
from Logging.PrintLog import Log
from Plugins import Plugins


log = Log()


class UnjoinedList(Plugins):
    """
    插件名：UnjoinedList \n
    插件类型：群聊插件 \n
    插件功能：使用未入群名单检查指令后输出未入群名单 \n
    """

    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "UnjoinedList"
        self.type = "Group"
        self.author = "kiriko"
        self.introduction = """
                                插件描述：使用名片检查指令后检查名片
                                插件功能：检查群名片
                            """
        self.init_status()
        self.all_stu_info = None

    async def main(self, event: GroupMessageEvent, debug):

        enable = self.config.get("enable")

        if not self.bot.database_enable:
            self.set_status("disable")
            return
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")
        if self.all_stu_info is None:
            while True:
                try:
                    self.all_stu_info = await self.select_all_info()
                    log.debug("初始化学生名单信息成功", debug)
                    break
                except Exception as e:
                    log.debug(e, debug=debug)
                    continue

        message1: str = event.message
        command_list = message1.split(" ")
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
                try:
                    self.api.groupService.send_group_msg(group_id=group_id,
                                                               message=f"该功能未在此群{group_id}生效")
                except Exception as e:
                    log.error(f"插件：{self.name}运行时出错：{e}")
                else:
                    log.debug(f"插件：{self.name}运行正确，成功向{group_id}发送了一条消息：该功能未在此群{group_id}生效",
                              debug)
                return
            else:
                operator_list = event.card.split("-")
                check_23: bool = self.config.get("check_23")
                if len(operator_list) == 3:
                    operator_role = operator_list[1]
                    if operator_role != "助教" and operator_role != "围观":
                        self.api.groupService.send_group_msg(group_id=group_id, message="你无权使用此功能")
                        return
                else:
                    if event.user_id == 278787983:  # 这个是渣哥的QQ号
                        pass

                group_member_list = (self.api.GroupService.get_group_member_list(self, group_id=group_id)).get(
                    "data")
                group_name = self.api.GroupService.get_group_info(self, group_id=group_id).get(
                    "data").get("group_name")
                match = re.search(r'高程(.*)实验群', group_name)
                if match:
                    class_part = match.group(1)
                    class_numbers = re.findall(r'\d{2}', class_part)
                    stu_in_class = {}
                    for number in class_numbers:
                        number = "100717" + number
                        for stu_id, stu_info in self.all_stu_info.get("data").items():
                            if stu_info["experiment"] == number:
                                stu_in_class[stu_id] = stu_info
                else:
                    stu_in_class = self.all_stu_info.get("data")

                for member in group_member_list:
                    card_cuts = member['card'].split("-")
                    try:
                        stu_id = int(card_cuts[0])
                    except:  # 学号不是纯数字
                        continue
                    select_result = stu_in_class.get(stu_id)
                    if select_result:
                        stu_in_class[int(stu_id)]['is_present'] = True

                # 获取消息并在排序后分组发送
                message: str = ""
                grouped_messages = []

                message2 = "以下在选课名单内的同学还未进群：\n"
                grouped_messages.append(message2)
                for stu_id, stu_info in stu_in_class.items():
                    if not stu_info['is_present']:
                        message3 = f"学号：{stu_id} 姓名：{stu_info['name']} \n"
                        grouped_messages.append(message3)
                try:
                    # 每20条为一组发送（包括不足20条的最后一组）
                    for i in range(0, len(grouped_messages), 20):
                        batch_message = "".join(grouped_messages[i:i + 20])
                        if batch_message:  # 确保有消息才发送
                            self.api.groupService.send_group_msg(group_id=group_id, message=batch_message)

                except Exception as e:
                    log.error(f"插件：{self.name}运行时出错：{e}")
                else:
                    log.debug(f"插件：{self.name}运行正确，成功向{group_id}发送了一条消息：{grouped_messages}", debug)

        return

    async def select_all_info(self):
        async_sessions = sessionmaker(
            bind=self.bot.database,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with async_sessions() as sessions:
            raw_table = select(self.StuInformation)
            results = await sessions.execute(raw_table)

            indexs = results.scalars().all()
            indexs_dict = {lc.stu_id: {'name': lc.name, 'major_short': lc.major, 'is_present': False,
                                       'experiment': lc.experiment} for lc in indexs}

            return {'data': indexs_dict}

    Basement = declarative_base()

    class StuInformation(Basement):
        __tablename__ = 'stu_information'
        stu_id = Column(Integer, primary_key=True)
        name = Column(String)
        major = Column(String)
        experiment = Column(String)
        #ingroup = Column(Integer)