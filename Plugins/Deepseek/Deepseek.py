import csv
from logging import log
import os
from CQMessage import CQHelper
from CQMessage.CQType import At 
from Plugins import Plugins
from openai import OpenAI
from Logging.PrintLog import Log

log = Log()

class Deepseek(Plugins):
    """
    这是一个插件的模板，开发一个新的插件至少应该包含以下部分
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "Deepseek"  # 插件的名字（一定要和类的名字完全一致（主要是我能力有限，否则会报错））
        self.type = "Group"  # 插件的类型（这个插件是在哪种消息类型中触发的）
        self.author = "budenghao"  # 插件开发作者（不用留真名，但是当插件报错的时候需要根据这个名字找到对应的人来修）
        self.introduction = """
                                配置文件：
                                    enable = True 默认打开
                                    use_bot_name 考虑到实际使用已移除
                                    effected_group = 生效的群号
                                    command = deepseek 看你心情改
                                    exclude = False 跳过加载项,不要的话就true
                                    op_id = 管理员名单,自己调用不限制
                                    base_url = https://api.deepseek.com 这个不需要改
                                    api_key = 自己到deepseek-api申请去
                                    csv_file = 统计使用次数文件
                                    limit_count = 限制使用次数
                                    limit_len = 为防刷屏,限制输出长度,超过就不输出(待做)
                                    op_id = 管理员id(白名单，仅限一个)
                                    
                            """
        self.init_status()

    def update_call_count(self, group_id: str, sender_id: str) -> bool:
        """
        更新调用次数
        :param sender_id: 调用者的 QQ 号
        """
        csv_file = self.config.get('csv_file')
        limit_count = self.config.get('limit_count')
        rows = []
        sender_id = str(sender_id)
        found = False
        if sender_id == self.config.get('op_id'):
            return True
        # 读取 CSV 文件
        try:
            if os.path.exists(csv_file):
                with open(csv_file, mode="r", newline="", encoding="gbk") as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row["sender_id"] == sender_id:
                            if int(row["call_count"]) >= int(limit_count):
                                self.api.groupService.send_group_msg(group_id=group_id,
                                                                     message=f"{At(qq=sender_id)}"+"\n已达到今日上限")
                                return False
                            row["call_count"] = str(int(row["call_count"]) + 1)  # 调用次数加 1
                            found = True
                        rows.append(row)
            else:
                return False
            # 如果 sender_id 不存在，添加新行
            if not found:
                rows.append({"sender_id": sender_id, "call_count": "1"})

            # 写回 CSV 文件
            with open(csv_file, mode="w", newline="", encoding="gbk") as file:
                writer = csv.DictWriter(file, fieldnames=["sender_id", "call_count"])
                writer.writeheader()
                writer.writerows(rows)
            return True
        
        except Exception as e:
            return False

    async def main(self, event, debug):
        """
        函数的入口，每个插件都必须有一个主入口 \n
        受到框架限制，所有插件的main函数的参数必须是这几个，不能多也不能少 \n
        注意！所有的插件都需要写成异步的方法，防止某个插件出问题卡死时导致整个程序阻塞
        :param event: 消息事件体
        :param debug: 是否输出debug信息
        :param config: 配置文件对象
        :return:
        """
        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")

        #信息初始化
        group_id = event.group_id
        sender_id = str(event.user_id)  # 获取发消息者的 QQ 号
        message: str = event.message
        command_list = message.split(" ")
        len_of_command = len(command_list)
        command = self.config.get("command")
        op_id = str(self.config.get("op_id"))
        
        #api初始化
        api_key=self.config.get("api_key")
        base_url = self.config.get("base_url")
        effected_group: list = self.config.get("effected_group")
        limit_len :int=self.config.get("limit_len")
        #没有指令或小于2直接return
        if len_of_command < 2 or command_list[0] != command:
            return
        if group_id not in effected_group:
            self.api.groupService.send_group_msg(group_id=group_id, message=f"该功能未在此群{group_id}生效")
            return
        
        try:
            client = OpenAI(api_key = api_key, base_url=base_url)
            is_limited:bool = False
            if sender_id == op_id:
                is_limited = False
                
            else:
                is_limited = not self.update_call_count(group_id,sender_id)
            if is_limited:
                 return
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "user", "content": command_list[1]},
                ],
                stream=False
            )
            self.api.groupService.send_group_msg(group_id=group_id, 
                                                message=f"{At(qq=sender_id)}"+"\n"+response.choices[0].message.content)
            # print((response)) #TO DO：长文本限制没做
            # if len(response.choices[0].message.content)<= limit_len:
            #     self.api.groupService.send_group_msg(group_id=group_id, 
            #                                     message=f"{At(qq=sender_id)}"+"\n"+response.choices[0].message.content)
            # else:
            #     self.api.groupService.send_group_msg(group_id=group_id, 
            #                                     message=f"{At(qq=sender_id)}"+"\n对不起,回复文本太长了")
            # log.debug(f"deepseek 插件成功回复")
            return
        except Exception as e:
            #  log.error(f"deepseek 插件出错：{e}")
             return