from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from Event.EventHandler.GroupMessageEventHandler import GroupMessageEvent
from Logging.PrintLog import Log
from Plugins import Plugins

log = Log()


class AddStuToDB(Plugins):
    """
    插件名：AddStuToDB \n
    插件类型：群聊插件 \n
    插件功能：将指定群的群成员作为学生信息导入到数据库中 \n
    插件指令：<bot> add_stu (debug) \n
    这是一个展示与数据库交互操作的示例插件，同时也进一步展示了插件从main入口开始调用不同的方法协同执行功能 \n
    这个插件本身没有什么实际意义，但是可以作为后续插件开发的参考（如果需要使用数据库操作） \n
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "AddStuToDB"
        self.type = "Group"
        self.author = "just monika"
        self.introduction = """
                                这是一个展示与数据库交互操作的示例插件，同时也进一步展示了插件从main入口开始调用不同的方法协同执行功能
                                这个插件本身没有什么实际意义，但是可以作为后续插件开发的参考（如果需要使用数据库操作）
                                插件功能：将指定群的群成员作为学生信息导入到数据库中
                                插件触发指令：<bot_name> add_stu (debug)
                            """
        self.init_status()

    async def main(self, event: GroupMessageEvent, debug):
        # 对于涉及与数据库交互的插件，如果数据库功能没开启，则强制禁用该插件
        if not self.bot.database_enable:
            self.set_status("disable")
            return
        # 首先判断该插件是否被启用，为否则直接退出
        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")
        # 获取消息，检查是否为指定的触发命令
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
            log.debug(f"开始执行插件：{self.name}", debug)
            from_group_id = event.group_id  # 获取发送命令的那个群的群号，后面要将执行结果反馈到该群
            try:  # 使用try-except来捕获异常，方便日志输出
                if len_of_command == 2:
                    group_id = event.group_id
                    effected_group: list = self.config.get("effected_group")
                    if str(group_id) not in effected_group:  # 在正常模式下，如果不是在指定的群内触发该命令，则不触发该插件
                        log.debug(f"{self.name}：pass", debug)
                        return
                    log.debug("以正常模式执行", debug)
                    await self.normal_mode(group_id)
                elif len_of_command == 3:
                    if command_list[2] == "debug":
                        log.debug("以debug模式执行", debug)
                        group_id = self.config.get("debug_group")
                        await self.debug_mode(group_id)
            except Exception as e:
                self.api.groupService.send_group_msg(from_group_id, message="命令执行失败！请查看输出日志")
                raise e
            else:
                log.debug(f"插件：{self.name}运行正确！", debug)
                self.api.groupService.send_group_msg(from_group_id, message="成功执行添加指令")

    async def normal_mode(self, group_id):
        # 把debug版本修改一下就行，这里不再重复演示
        ...

    async def debug_mode(self, group_id):
        """
        add_stu的debug模式，使用配置文件中指定的debug_group作为示例
        :param group_id:
        :return:
        """
        # 通过api获取该群的群成员名单，并且进行处理后封装为类
        res = await self.api.groupService.get_group_member_list(group_id)
        student_info_list = self.handle_response(res)

        # 使用异步方法将获取到的名单全部添加到bot数据库的student_info表中
        try:
            await self.add_student_info_into_db(student_info_list)
        except Exception as e:
            raise e

    def handle_response(self, response):
        """
        将从api中获取到的原始数据进行处理，使其能够封装成一个对象以方便后续与数据库进行交互
        :param response: 原始的响应数据
        :return:
        """
        # print(response)
        # 先定义一个空的列表，后面用它来储存每个student对象
        student_info_list = []

        # 从原始数据中获得需要的那一部分数据
        member_list = response.get("data")
        for member in member_list:  # 通过遍历将每个群成员信息进行提取和封装
            user_id = member.get("user_id")
            nickname = member.get("nickname")
            card = member.get("card")
            sex = member.get("sex")
            age = member.get("age")
            # 这个StudentInfo类在最下面定义，是专门用于和数据库交互的子类
            student = self.StudentInfo(userId=user_id,
                                       nickname=nickname,
                                       card=card,
                                       sex=sex,
                                       age=age
                                       )
            student_info_list.append(student)
            # print(student)

        return student_info_list

    async def add_student_info_into_db(self, student_info_list):
        # 先创建一个异步(async)的与数据库的操作对象
        AsyncSessionLocal = sessionmaker(
            bind=self.bot.database,
            class_=AsyncSession,
            expire_on_commit=False
        )

        # 使用异步的方法与数据库进行交互
        async with AsyncSessionLocal() as session:
            async with session.begin():
                for student in student_info_list:
                    student_data = {
                        'userId': student.userId,
                        'nickname': student.nickname,
                        'card': student.card,
                        'age': student.age,
                        'sex': student.sex
                    }
                    # 创建一个INSERT语句，它的.values()方法只能接收dict类型的变量，因此上面需要将封装好的对象的数据先提取出来
                    stmt = insert(self.StudentInfo).values(**student_data)
                    # 添加ON DUPLICATE KEY UPDATE（即当主键重复时，如何处理其他数据--在MySQL中，主键（也叫唯一键）是不允许有重复的）
                    update_dict = {k: v for k, v in student_data.items() if k != 'user_id'}
                    stmt = stmt.on_duplicate_key_update(**update_dict)
                    await session.execute(stmt)  # 执行插入
                await session.commit()

    Base = declarative_base()

    class StudentInfo(Base):
        """
        这个类就是用来封装学生数据的类
        """
        __tablename__ = 'student_info'  # 数据库中的表名

        userId = Column(BigInteger, primary_key=True)
        nickname = Column(String(64))
        card = Column(String(64))
        age = Column(Integer)
        sex = Column(String(8))

        def __repr__(self):
            return f"<StudentInfo(userId={self.userId}, nickname={self.nickname}, card={self.card}, age={self.age}, sex={self.sex})>"




