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


class CardComf(Plugins):
    """
    插件名：CardComf \n
    插件类型：群聊插件 \n
    插件功能：使用名片检查指令后检查名片 \n
    """

    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "CardComf"
        self.type = "Group"
        self.author = "kiriko"
        self.introduction = """
                                插件描述：使用名片检查指令后检查名片
                                插件功能：检查群名片
                            """
        self.init_status()
        self.all_stu_info = None
        self.at: bool = self.config.get('at')
        self.threshold = self.config.get('threshold')
        self.kick: bool = self.config.get('kick')
        self.kick_type2: bool = self.config.get('kick_type2')
        self.check_not_present: bool = self.config.get('check_not_present')
        self.check_major: bool = self.config.get('check_major')

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
        check_with_stu_list = self.config.get("check_with_stu_list")
        check_assistants = self.config.get("check_assistants")
        self.at: bool = self.config.get('at')
        self.threshold = self.config.get('threshold')
        self.kick: bool = self.config.get('kick')
        self.kick_type2: bool = self.config.get('kick_type2')
        self.check_not_present: bool = self.config.get('check_not_present')
        self.check_major: bool = self.config.get('check_major')

        if check_with_stu_list:
            if self.all_stu_info is None:
                while True:
                    try:
                        self.all_stu_info = await self.select_all_infom()
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
                school_lists: list = self.config.get("school_lists")
                major_lists: list = self.config.get("major_lists")
                assistants_list = self.handle_raw_list(self.get_assistant_raw_list())
                operator_list = event.card.split("-")
                check_23: bool = self.config.get("check_23")
                if len(operator_list) == 3:
                    operator_role = operator_list[1]
                    if operator_role != "助教" and operator_role != "围观":
                        self.api.groupService.send_group_msg(group_id=group_id, message="你无权使用此功能")
                        return
                    else:
                        if self.is_assistant(event.user_id, assistants_list):
                            pass
                        else:
                            self.api.groupService.send_group_msg(group_id=group_id, message="big胆，敢冒充助教")
                            return
                else:
                    if event.user_id == 278787983:  # 这个是渣哥的QQ号
                        pass
                    else:
                        self.api.groupService.send_group_msg(group_id=group_id, message="连自己名片都改不对还想检查别人名片？")
                        return

                group_member_list = (self.api.GroupService.get_group_member_list(self, group_id=group_id)).get(
                    "data")
                ingored_ids: list = self.config.get("ignored_ids")

                user_ids = []
                legality = {}
                if self.kick_type2:
                    kick_type2_ids = []
                for members in group_member_list:
                    user_id = members['user_id']
                    legality[f'{user_id}'] = 1
                    if members['user_id'] in ingored_ids:
                        continue
                    card_cuts = members['card'].split("-")
                    if len(card_cuts) != 3:
                        legality[f'{user_id}'] = 0  # 代表群名片没有分三项
                    else:
                        try:
                            stu_id = int(card_cuts[0])
                        except:  # 学号不是纯数字
                            legality[f'{user_id}'] = -6
                            continue
                        if " " in card_cuts[0]:  # 学号不是纯数字
                            legality[f'{user_id}'] = -6
                        if stu_id // 1000000 == 0 or stu_id // 1000000 > 2:  # 学号不是七位或者数值有误
                            legality[f'{user_id}'] = -6
                            continue
                        stu_major = card_cuts[1]
                        stu_major = re.sub(r'\d', '', stu_major)
                        stu_name = card_cuts[2]
                        if stu_major == "助教" or stu_major == "围观":
                            if check_assistants:
                                if self.is_assistant(user_id, assistants_list):
                                    pass
                                else:
                                    legality[f'{user_id}'] = -5  # 代表冒充助教或者没有进助教群的助教
                            continue

                        if check_with_stu_list:  # 启用核对学生名单的情况
                            select_result = None
                            try:
                                data = self.all_stu_info.get("data")
                                select_result = data.get(stu_id)
                            except Exception as e:
                                raise e
                            if select_result:
                                query_name = select_result.get("name")
                                if '·' in query_name:
                                    query_name1 = query_name.split('·')[0]
                                else:
                                    query_name1 = query_name
                                if self.check_major:
                                    query_major = select_result.get("major_short")  # 指专业简写
                                    if "强" in query_major:
                                        query_major.replace("强", "")
                                    query_group = select_result.get("ingroup")  # 指的是信xx中的xx
                                    full_major = ""

                                    if not query_group:
                                        full_major += query_major
                                    else:
                                        full_major += query_major + (
                                            f"0{query_group}" if query_group < 10
                                            else str(query_group))  # 这一步是确定学生的专业名称

                                school_lists: list = self.config.get("school_lists")
                                stu_id = card_cuts[0]
                                if stu_name != query_name:  # 代表学生名字和学号不对应
                                    if query_name1:
                                        if stu_name != query_name1:
                                            legality[f'{user_id}'] = -1
                                    else:
                                        legality[f'{user_id}'] = -1
                                if stu_id.startswith("2456"):  # 对留学生进行特判
                                    pass
                                elif stu_id.startswith("24"):
                                    if stu_major not in school_lists:
                                        legality[f'{user_id}'] = -4
                                    if self.check_major:
                                        if stu_major != full_major:  # 代表学生的专业名称与学生名单中的信息不对应
                                            legality[f'{user_id}'] = -2
                                else:  # 将降转和应届学生区分
                                    if self.is_assistant(user_id, assistants_list):  # 在助教群但没有更改为助教或围观
                                        legality[f'{user_id}'] = -7
                                    elif stu_major not in school_lists:
                                        if check_23:  # 启用核对23届信息的情况
                                            if stu_id.startswith("2356"):  # 对留学生进行特判
                                                continue
                                            legality[f'{user_id}'] = -4
                                        else:
                                            legality[f'{user_id}'] = 1
                                    elif self.check_major:
                                        if stu_major != full_major:  # 代表学生的专业名称与学生名单中的信息不对应
                                            legality[f'{user_id}'] = -2
                                self.all_stu_info['data'][int(stu_id)]['is_present'] = True
                            else:  # 代表学生名单中没有这个学号的信息
                                legality[f'{user_id}'] = -3
                                if self.kick_type2:
                                    kick_type2_ids.append(user_id)
                        else:
                            stu_id = card_cuts[0]
                            if stu_id.startswith("24"):
                                if stu_id.startswith("2456"):  # 对留学生进行特判
                                    continue
                                elif stu_major not in school_lists:
                                    legality[f'{user_id}'] = -4
                            else:  # 将降转和应届学生区分
                                if self.is_assistant(user_id, assistants_list):  # 在助教群但没有更改为助教或围观
                                    legality[f'{user_id}'] = -7
                                elif stu_major not in major_lists:
                                    if check_23:  # 启用核对23届信息的情况
                                        legality[f'{user_id}'] = -4
                                    else:
                                        legality[f'{user_id}'] = 1

                for members in group_member_list:
                    user_id = members['user_id']
                    if legality[f'{user_id}'] != 1:
                        user_ids.append(members['user_id'])

                while True:
                    try:
                        user_counts_map = await self.increment_counts_for_users(user_ids, debug)
                        break
                    except Exception as e:
                        log.debug(e, debug=debug)

                # 获取消息并在排序后分组发送
                message: str = ""
                grouped_raw_messages = {}  # 用来存储分组的消息
                for members in group_member_list:
                    user_id = members['user_id']
                    if legality[f'{user_id}'] != 1:
                        message, counts = self.message_generate(legality=legality, members=members,
                                                                user_counts_map=user_counts_map)
                        if message != "":
                            grouped_raw_messages[message] = counts
                            message = ""

                grouped_raw_messages["请以下同学尽快修改群名片:"] = 99999
                sorted_messages = dict(sorted(
                    grouped_raw_messages.items(),
                    key=lambda item: item[1],  # 按照警告次数排序
                    reverse=True  # 降序
                ))
                grouped_messages = list(sorted_messages.keys())

                if self.check_not_present:
                    message2 = "以下在选课名单内的同学还未进群：\n"
                    grouped_messages.append(message2)
                    for stu_id, stu_info in self.all_stu_info['data'].items():
                        if not stu_info['is_present']:
                            message3 = f"学号：{stu_id} 姓名：{stu_info['name']} \n"
                            grouped_messages.append(message3)
                kicks = 0

                try:
                    # 每20条为一组发送（包括不足20条的最后一组）
                    for i in range(0, len(grouped_messages), 20):
                        batch_message = "".join(grouped_messages[i:i + 20])
                        if batch_message:  # 确保有消息才发送
                            self.api.groupService.send_group_msg(group_id=group_id, message=batch_message)

                    for members in group_member_list:
                        if self.kick:
                            if user_counts_map[members['user_id']] == int(self.threshold):
                                self.api.groupService.set_group_kick(group_id=group_id,
                                                                           user_id=members['user_id'])
                                kicks += 1

                    if self.kick_type2:
                        for id_ in kick_type2_ids:
                            self.api.groupService.set_group_kick(group_id=group_id,
                                                                 user_id=id_)

                except Exception as e:
                    log.error(f"插件：{self.name}运行时出错：{e}")
                else:
                    log.debug(f"插件：{self.name}运行正确，成功向{group_id}发送了一条消息：{grouped_messages}", debug)
                    if kicks > 0:
                        log.debug(f"插件：{self.name}运行正确，成功将{group_id}的违规次数到达阈值的成员移出群聊", debug)

        return

    def message_generate(self, legality, members, user_counts_map):
        mem_id = members['user_id']
        message = ""
        if self.at:
            message += f"[CQ:at,qq={members['user_id']}]"
        else:
            message += f"qq号：{members['user_id']}"
        if legality[f'{mem_id}'] == 0:
            message += f"，名片:{members['card']},名片未用-分为三项,提醒次数为{user_counts_map[members['user_id']]}"
        elif legality[f'{mem_id}'] == -1:
            message += f"，名片:{members['card']},学号与姓名不符,提醒次数为{user_counts_map[members['user_id']]}"
        elif legality[f'{mem_id}'] == -2:
            card_cuts = members['card'].split("-")
            stu_id = int(card_cuts[0])
            select_result = None
            try:
                data = self.all_stu_info.get("data")
                select_result = data.get(stu_id)
            except Exception as e:
                raise e
            query_major = select_result.get("major_short")
            query_group = select_result.get("ingroup")
            full_major = ""
            if not query_group:
                full_major += query_major
            else:
                full_major += query_major + (f"0{query_group}" if query_group < 10 else str(query_group))
            message += f"，名片:{members['card']},专业名称({card_cuts[1]})与名单册的信息({full_major})不符,提醒次数为{user_counts_map[members['user_id']]}"
        elif legality[f'{mem_id}'] == -3:
            message += f"，名片:{members['card']},该学号未在学生名单中,提醒次数为{user_counts_map[members['user_id']]}"
        elif legality[f'{mem_id}'] == -4:
            message += f"，名片:{members['card']},托管学院或专业名称不正确,提醒次数为{user_counts_map[members['user_id']]}"
        elif legality[f'{mem_id}'] == -5:
            message += f"，名片:{members['card']}，未在助教群中找到对应的QQ号,提醒次数为{user_counts_map[members['user_id']]}"
        elif legality[f'{mem_id}'] == -6:
            message += f"，名片:{members['card']}，学号格式错误,提醒次数为{user_counts_map[members['user_id']]}"
        if self.kick:
            if user_counts_map[members['user_id']] == int(self.threshold):
                message += ",移出群聊"
        message += "\n"
        return message, user_counts_map[members['user_id']]

    @classmethod
    def is_assistant(cls, user_id, assistant_list):
        return user_id in assistant_list

    def get_assistant_raw_list(self):
        group_id = self.config.get("assistants_group")
        return self.api.groupService.get_group_member_list(group_id=group_id).get("data")

    @classmethod
    def handle_raw_list(cls, raw_list):
        assistants_user_id_list = []
        for info in raw_list:
            user_id = info.get("user_id")
            assistants_user_id_list.append(user_id)

        return assistants_user_id_list

    async def select_all_infom(self):
        async_sessions = sessionmaker(
            bind=self.bot.database,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with async_sessions() as sessions:
            raw_table = select(self.stu_information)
            results = await sessions.execute(raw_table)

            indexs = results.scalars().all()
            if self.check_major:
                indexs_dict = {lc.stu_id: {'name': lc.name, 'major_short': lc.major, 'is_present': False} for lc in indexs}
            else:
                indexs_dict = {lc.stu_id: {'name': lc.name, 'is_present': False} for lc in
                           indexs}


            return {'data': indexs_dict}

    async def increment_counts_for_users(self, user_ids, debug):
        """
        对一组已有初值的 user_id 批量执行 counts 增量更新（所有增量为 1），对未设初值的进行设置，并返回更新后的 counts 映射
        """

        async_sessions = sessionmaker(
            bind=self.bot.database,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with async_sessions() as session:
            async with session.begin():
                # 查询所有相关用户的当前 counts 值
                stmt = select(self.warn_counts).where(self.warn_counts.user_id.in_(user_ids))
                try:
                    result = await session.execute(stmt)
                except Exception as e:
                    raise Exception("Retry") from e
                log.debug("初始化计数信息成功", debug)
                user_records = result.scalars().all()

                # 构建 user_id 到 counts 的映射
                user_counts_map = {user.user_id: user.counts for user in user_records}

                # 批量更新
                for user_id in user_ids:
                    if user_id in user_counts_map:

                        new_counts = user_counts_map[user_id] + 1
                        update_stmt = (
                            update(self.warn_counts).
                            where(self.warn_counts.user_id == user_id).
                            values(counts=new_counts)
                        )
                        await session.execute(update_stmt)
                        # 更新映射中的 counts
                        user_counts_map[user_id] = new_counts
                    else:
                        #更新未曾录入的用户
                        new_counts = 1
                        add_stmt = self.warn_counts(
                            user_id=user_id,
                            counts=new_counts
                        )
                        session.add(add_stmt)
                        # 更新映射中的 counts
                        user_counts_map[user_id] = new_counts

                if self.kick:
                    for user_id in user_ids:
                        if user_id in user_counts_map:
                            if user_counts_map[user_id] == int(self.threshold):
                                delete_stmt = (
                                    delete(self.warn_counts).
                                    where(self.warn_counts.user_id == user_id)
                                )
                                await session.execute(delete_stmt)
                                # 将被踢出群聊的用户的计数信息删除

                # 最后一次性提交所有更改
                await session.commit()
                if self.kick:
                    log.debug("已将所有被警告的用户对应的警告次数计数加一,并删除了提醒次数到达阈值的的用户的计数数据")
                else:
                    log.debug("已将所有被警告的用户对应的警告次数计数加一")

        return user_counts_map

    Basement = declarative_base()

    class stu_information(Basement):
        __tablename__ = 'stu_information'
        stu_id = Column(Integer, primary_key=True)
        name = Column(String)
        major = Column(String)
        #ingroup = Column(Integer)

    class warn_counts(Basement):
        __tablename__ = 'warn_counts'
        user_id = Column(BigInteger, primary_key=True)
        counts = Column(Integer)
