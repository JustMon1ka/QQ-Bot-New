from Event.EventHandler.PrivateMessageEventHandler import PrivateMessageEvent
from Event.EventHandler.GroupMessageEventHandler import GroupMessageEvent
from Logging.PrintLog import Log
from CQMessage.CQType import At
from Plugins import Plugins
import requests
import re
log=Log()

class DailyWord(Plugins):


    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "DailyWord"  # 插件的名字（一定要和类的名字完全一致（主要是我能力有限，否则会报错））
        self.type = "Group"  # 插件的类型（这个插件是在哪种消息类型中触发的）
        self.author = "x1x"  # 插件开发作者（不用留真名，但是当插件报错的时候需要根据这个名字找到对应的人来修）
        self.introduction = """
                                每日一词小程序^_^
                                可用命令：
                                word 注册青年大学习   注册
                                word 每日n词         练习拼写n个词
                                word 复习n词         练习拼写n个词（从已学习的词库中选取)
                                word 看答案          查看答案
                                word 取消           取消拼写
                                word <word>         提交答案
                            """
        self.init_status()

        self.cur_daily_word_owner_qq = None
        self.cur_word_num = 0
        self.commit_status = {}

    def send_message(self, event, message):
        self.api.groupService.send_group_msg(group_id=event.group_id, message=f"{At(qq=event.user_id)} {message}")

    def register(self, qq_id):
        params = {
            "user_qq": qq_id,
            "op_password": self.config.get("op_password")
        }
        response = requests.post(self.config.get('base_url')+'register', json=params)
        json_data = response.json()
        status, message = json_data.get("status"), json_data.get("message")
        if status == 'ok':
            log.info(f"daily_word: 用户{qq_id}注册成功，{message}")
            return '注册成功!'
        else:
            log.error(f"daily_word: 用户{qq_id}注册失败，{message}")
            if message == "user already registered":
                return "你已经注册过啦!"
            return "注册失败，请联系管理员!"


    def create_daily_word(self, user_qq, num, is_review=False):
        if self.cur_daily_word_owner_qq is not None:
            return f"目前{At(qq=self.cur_daily_word_owner_qq)}发起的每日一词还没结束！"
        params = {
            "user_qq": user_qq,
            "num": num,
            "is_review": is_review,
            "op_password": self.config.get("op_password")
        }
        response = requests.post(self.config.get('base_url') + 'create', json=params)
        json_data = response.json()
        status, message = json_data.get("status"), json_data.get("message")
        if status == 'ok':
            log.info(f"daily_word: 用户{user_qq}获取{num}个词成功(is_review={is_review})，{message}")
            self.cur_daily_word_owner_qq = user_qq
            self.cur_word_num = num
            result_message = "\n"
            for word in message:
                result_message += f"{word}\n"
            return result_message
        else:
            log.error(f"daily_word: 用户{user_qq}获取{num}个词失败(is_review={is_review})，{message}")
            if message == 'user not registered':
                return "你还没有注册，请先注册！"
            elif message == 'no word found' and is_review:
                return "孩子，你学过吗，就复习？"

            return "获取失败，请联系管理员！"


    def get_dictation(self, user_qq):
        if self.cur_daily_word_owner_qq is None:
            return "没有可以获取的提示诶..."
        params = {
            "user_qq": user_qq,
            "op_password": self.config.get("op_password")
        }
        response = requests.post(self.config.get('base_url') + 'dictation', json=params)
        json_data = response.json()
        status, message = json_data.get("status"), json_data.get("message")
        if status == 'ok':
            log.info(f"daily_word: 用户{user_qq}获取词典成功，{message}")
            result_message = ""
            for word in message:
                result_message += f"{word}\n"
            return result_message
        else:
            log.error(f"daily_word: 用户{user_qq}获取词典失败，{message}")
            if message == 'user not registered':
                return "你还没有注册，请先注册！"
            return "获取失败，请联系管理员！"

    def get_mvp(self):
        mvp = []
        max_count = 0
        for qq, count in self.commit_status.items():
            if len(mvp) == 0 or count > max_count:
                mvp = [str(At(qq))]
                max_count = count
            elif count == max_count:
                mvp.append(str(At(qq)))
        return ' '.join(mvp)

    def commit_word(self, committer_qq, word):
        if self.cur_daily_word_owner_qq is None:
            return "请先发起每日一词！"
        params = {
            "committer_qq": committer_qq,
            "owner_qq": self.cur_daily_word_owner_qq,
            "answer": word,
            "op_password": self.config.get("op_password")
        }
        response = requests.post(self.config.get('base_url') + 'commit', json=params)
        json_data = response.json()
        status, message = json_data.get("status"), json_data.get("message")
        if status == 'ok':
            log.info(f"daily_word: 用户{committer_qq}提交词{word}成功，每日一词创建者：{self.cur_daily_word_owner_qq}，{message}")
            result_message = "回答正确，👻🌶！"
            self.commit_status[committer_qq] = self.commit_status.get(committer_qq, 0) + 1
            if message == 'words all cleared':
                result_message += f'\n最后一词已被答对!'
                if self.cur_word_num > 1:
                    result_message += f'{self.get_mvp()}得了mvp!'
                self.cur_daily_word_owner_qq = None
                self.cur_word_num = 0
                self.commit_status = {}
            return result_message
        else:
            log.error(f"daily_word: 用户{committer_qq}提交词{word}失败，{message}")
            if message == 'user not registered':
                return "你还没有注册，请先注册！"
            elif message == 'wrong answer':
                return "回答错误，杂鱼~❤"
            else:
                return "提交失败，请联系管理员！"

    def see_the_answer(self):
        if self.cur_daily_word_owner_qq is None:
            return "没有可看的答案诶..."
        params = {
            "user_qq": self.cur_daily_word_owner_qq,
            "op_password": self.config.get("op_password")
        }
        response = requests.post(self.config.get('base_url') + 'answer', json=params)
        json_data = response.json()
        status, message = json_data.get("status"), json_data.get("message")
        if status == 'ok':
            log.info(f"daily_word: 用户{self.cur_daily_word_owner_qq}查看答案成功，{message}")
            result_message = "躺赢狗！\n"
            for word in message:
                result_message += f"{word}\n"
            return result_message
        else:
            log.error(f"daily_word: 用户{self.cur_daily_word_owner_qq}查看答案失败，{message}")
            return "查看失败，请联系管理员！"


    def cancel_daily_word(self):
        params = {
            "user_qq": self.cur_daily_word_owner_qq,
            "op_password": self.config.get("op_password")
        }
        response = requests.post(self.config.get('base_url') + 'cancel', json=params)
        json_data = response.json()
        status, message = json_data.get("status"), json_data.get("message")
        if status == 'ok':
            log.info(f"daily_word: 用户{self.cur_daily_word_owner_qq}取消每日一词成功，{message}")
            self.cur_daily_word_owner_qq = None
            self.commit_status = {}
            return "取消成功！"
        else:
            log.error(f"daily_word: 用户{self.cur_daily_word_owner_qq}取消每日一词失败，{message}")
            return "取消失败，请联系管理员！"



    @staticmethod
    def get_word_num(s):
        pattern = re.compile(r'每日(\d+)词')
        match = pattern.search(s)
        if match:
            return int(match.group(1))
        return 0

    @staticmethod
    def get_review_num(s):
        pattern = re.compile(r'复习(\d+)词')
        match = pattern.search(s)
        if match:
            return int(match.group(1))
        return 0

    async def main(self, event, debug):
        """
        函数的入口，每个插件都必须有一个主入口 \n
        受到框架限制，所有插件的main函数的参数必须是这几个，不能多也不能少 \n
        注意！所有的插件都需要写成异步的方法，防止某个插件出问题卡死时导致整个程序阻塞
        :param event: 消息事件体
        :param debug: 是否输出debug信息
        :return:
        """

        # 检查是否启用插件
        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return
        # 检查是否为生效群聊
        group_id = event.group_id
        if group_id not in self.config.get("effected_group"):
            self.api.groupService.send_group_msg(group_id=group_id, message=f"该功能未在此群{group_id}生效")
            return
        if self.status != "error":
            self.set_status("running")
        # 是否触发关键词
        message = event.message  # [{'type': 'text', 'data': {'text': 'hello'}}]
        try:
            if message[0]['type'] == 'text':
                content = message[0]['data']['text'].split()
                if len(content) < 2 or content[0] != self.config.get("command"):
                    return
            else:
                return
        except Exception as e:
            log.error(f"daily_word: 解析消息失败，{e}")
            return

        # 解析参数
        user_id = event.user_id
        log.debug(f"插件：{self.name}收到一条消息：{message}，来自{user_id}", debug)
        if content[1] == "注册青年大学习":    # 注册青年大学习
            log.debug(f"daily_word: 用户{user_id}注册青年大学习", debug)
            self.send_message(event, self.register(user_id))
        elif word_num := self.get_word_num(content[1]):  # 每日n词
            log.debug(f"daily_word: 用户{user_id}获取{word_num}个词", debug)
            self.send_message(event, self.create_daily_word(user_id, word_num, False))
        elif word_num := self.get_review_num(content[1]):  # 复习n词
            log.debug(f"daily_word: 用户{user_id}获取{word_num}个词(复习)", debug)
            self.send_message(event, self.create_daily_word(user_id, word_num, True))
        elif content[1] == "看答案":    # 查看答案
            log.debug(f"daily_word: 用户{user_id}查看答案", debug)
            self.send_message(event, self.see_the_answer())
        elif content[1] == "取消":    # 取消
            log.debug(f"daily_word: 用户{user_id}取消每日一词", debug)
            self.send_message(event, self.cancel_daily_word())
        else:  # 提交 something
            log.debug(f"daily_word: 用户{user_id}提交词{content[1]}", debug)
            self.send_message(event, self.commit_word(user_id, content[1]))

        return