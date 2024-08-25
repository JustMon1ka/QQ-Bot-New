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
        self.all_line_count = None
        self.at: bool = self.config.get('at')
        self.threshold = self.config.get('threshold')
        self.kick: bool = self.config.get('kick')

    async def main(self, event, debug):

        enable = self.config.get("enable")

        if not self.bot.database_enable:
            self.set_status("disable")
            return
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")

        if self.all_line_count is None:
            while True:
                try:
                    self.all_line_count = await self.select_all_infom()
                    log.debug("初始化名片信息成功", debug)
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
            major_lists: list = self.config.get("major_lists")

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
                group_memberlist = (self.api.GroupService.get_group_member_list(self, group_id=group_id)).get(
                    "data")
                ingored_ids: list = self.config.get("ignored_ids")

                user_ids = []
                legality = {}

                for members in group_memberlist:
                    mem_id = members['user_id']
                    legality[f'{mem_id}'] = 1
                    if members['user_id'] in ingored_ids:
                        continue
                    card_cuts = members['card'].split("-")
                    if len(card_cuts) != 3:
                        legality[f'{mem_id}'] = 0
                    else:
                        stu_id = int(card_cuts[0])
                        select_result = None
                        try:
                            data = self.all_line_count.get("data")
                            select_result = data.get(stu_id)
                        except Exception as e:
                            raise e
                        if select_result:
                            query_name = select_result.get("name")
                            query_major = select_result.get("major_short")
                            query_group = select_result.get("ingroup")
                            full_major = ""
                            stu_major = re.sub(r'\d', '', card_cuts[1])

                            if not query_group:
                                full_major += query_major
                            else:
                                full_major += query_major + (
                                    f"0{query_group}" if query_group < 10 else str(query_group))

                            if card_cuts[2] != query_name:
                                legality[f'{mem_id}'] = -1
                            elif stu_major not in major_lists:
                                legality[f'{mem_id}'] = -4
                            elif card_cuts[1] != full_major:
                                legality[f'{mem_id}'] = -2
                        else:
                            legality[f'{mem_id}'] = -3

                for members in group_memberlist:
                    mem_id = members['user_id']
                    if legality[f'{mem_id}'] != 1:
                        user_ids.append(members['user_id'])

                while True:
                    try:
                        user_counts_map = await self.increment_counts_for_users(user_ids, debug)
                        break
                    except Exception as e:
                        log.debug(e, debug=debug)

                message: str = ""
                for members in group_memberlist:
                    mem_id = members['user_id']
                    if legality[f'{mem_id}'] != 1:
                        message += self.message_generate(legality=legality, members=members,
                                                         user_counts_map=user_counts_map)

                kicks = 0
                try:
                    self.api.groupService.send_group_msg(group_id=group_id, message=message)
                    for members in group_memberlist:
                        if kicks:
                            if user_counts_map[members['user_id']] == int(self.threshold):
                                self.api.groupService.set_group_kick(group_id=group_id,
                                                                           user_id=members['user_id'])
                                kicks += 1

                except Exception as e:
                    log.error(f"插件：{self.name}运行时出错：{e}")
                else:
                    log.debug(f"插件：{self.name}运行正确，成功向{group_id}发送了一条消息：{message}", debug)
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
                data = self.all_line_count.get("data")
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
            message += f"，名片:{members['card']}],学号格式不正确,提醒次数为{user_counts_map[members['user_id']]}"
        elif legality[f'{mem_id}'] == -4:
            message += f"，名片:{members['card']}],专业名称非法,提醒次数为{user_counts_map[members['user_id']]}"
        if self.kick:
            if user_counts_map[members['user_id']] == int(self.threshold):
                message += ",移出群聊"
        message += "\n"
        return message

    async def select_all_infom(self):
        async_sessions = sessionmaker(
            bind=self.bot.database,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with async_sessions() as sessions:
            raw_table = select(self.stu_imformation)
            results = await sessions.execute(raw_table)

            indexs = results.scalars().all()
            indexs_dict = {lc.stu_id: {'name': lc.name, 'major_short': lc.major_short, 'ingroup': lc.ingroup} for lc in
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

    class stu_imformation(Basement):
        __tablename__ = 'stu_imformation'
        stu_id = Column(Integer, primary_key=True)
        name = Column(String)
        major_short = Column(String)
        ingroup = Column(Integer)

    class warn_counts(Basement):
        __tablename__ = 'warn_counts'
        user_id = Column(BigInteger, primary_key=True)
        counts = Column(Integer)
