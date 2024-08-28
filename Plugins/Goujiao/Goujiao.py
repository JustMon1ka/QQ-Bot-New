import random
import re
import requests
from CQMessage.CQType import At 
from Plugins import Plugins


class Goujiao(Plugins):
    """
    这是一个插件的模板，开发一个新的插件至少应该包含以下部分
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "Goujiao"  # 插件的名字（一定要和类的名字完全一致（主要是我能力有限，否则会报错））
        self.type = "Group"  # 插件的类型（这个插件是在哪种消息类型中触发的）
        self.author = "budenghao"  # 插件开发作者（不用留真名，但是当插件报错的时候需要根据这个名字找到对应的人来修）
        self.introduction = """
                                对狗叫的人禁言
                                配置文件：
                                    enable = True 默认打开
                                    use_bot_name 考虑到实际已移除
                                    effected_group = 生效的群号
                                    command = 命令,不启用botname调用时发送 "@群成员 命令"触发狗叫制裁
                                    goujiao_warning =  触发后bot说的话
                                    bot_id = bot自己的QQ号
                                    op_id = 管理员id(白名单，仅限一个)
                                    duration = 禁言时间,单位为秒
                                    use_rand_time = 禁言时间是否小范围随机
                                    auto_detect =  是否自动检测狗叫(要使用校园网
                            """
        self.init_status()

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

        group_id = event.group_id
        sender_id = str(event.user_id)  # 获取发消息者的 QQ 号
        message: str = event.message
        command_list = message.split(" ")
        len_of_command = len(command_list)
        command = self.config.get("command")
        
        auto_detect = self.config.get("auto_detect") 
        duration = int(self.config.get("duration"))
        bot_id = str(self.config.get("bot_id"))
        op_id = str(self.config.get("op_id"))
        if self.config.get("use_rand_time"):
            duration *= random.randint(1, 3)
        effected_group: list = self.config.get("effected_group")
        all_reply_message: list = self.config.get("goujiao_warning")
        joined_string = " ".join(all_reply_message)  #分隔字符按需修改
        warning_prob = self.config.get("warning_prob")

        if auto_detect:
            url = "http://10.80.43.210:5555"
            request_data = {
            "message": message
            }
            res = requests.post(url, json=request_data)
            prob = res.json().get('Prob')
            result = res.json().get('Result')
            print("prob:"+str(prob)+"  result:"+str(result)) 
            #开启自动检测，只有检测到的时候会触发
            if prob >= float(warning_prob) and result == 1 :  
                        
                if group_id not in effected_group:
                    self.api.groupService.send_group_msg(group_id=group_id, message=f"该功能未在此群{group_id}生效")
                    return
                else:
                    #自己勾脚怎么能算勾脚呢( 
                    self.api.groupService.send_group_msg(group_id=group_id, message=f"{At(qq=sender_id)}"+"\n"+joined_string)
                    if sender_id != op_id:
                        self.api.groupService.set_group_ban(group_id=group_id, user_id=sender_id, duration=5)
                    return

           
        #没有指令或小于2直接return
        if len_of_command < 2 or command_list[1] != command:
            return
        #分是否启用bot_name两种情况
        
        at_pattern = re.compile(r'\[CQ:at,qq=(\d+)\]')  # 使用正则表达式提取被@的QQ号
        at_match = at_pattern.search(message)
        if at_match:
            at_id = at_match.group(1)  # 提取到的QQ号
            if at_id == bot_id or at_id == op_id: #试图禁言机器人触发反甲彩蛋
                self.api.groupService.set_group_ban(group_id=group_id, user_id=sender_id, duration=duration)
                self.api.groupService.send_group_msg(group_id=group_id, message=f"{At(qq=sender_id)}"+"\n 还想搞我?没门")
                return
        else:
            return  # 如果没有@某人，则返回
        if group_id not in effected_group:
            self.api.groupService.send_group_msg(group_id=group_id, message=f"该功能未在此群{group_id}生效")
            return
        else:
            self.api.groupService.set_group_ban(group_id=group_id, user_id=at_id, duration=duration)
            self.api.groupService.send_group_msg(group_id=group_id, message=f"{At(qq=at_id)}"+"\n"+joined_string)
        return