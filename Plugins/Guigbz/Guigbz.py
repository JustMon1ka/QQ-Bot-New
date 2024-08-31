import aiohttp

from CQMessage.CQType import Record
from Plugins import Plugins
from Event.EventHandler import GroupMessageEventHandler
from Logging.PrintLog import Log
log= Log()

class Guigbz(Plugins):
    """
    这是一个插件的模板，开发一个新的插件至少应该包含以下部分
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "Guigbz"  # 插件的名字（一定要和类的名字完全一致（主要是我能力有限，否则会报错））
        self.type = "Group"  # 插件的类型（这个插件是在哪种消息类型中触发的）
        self.author = "Yuyu"  # 插件开发作者（不用留真名，但是当插件报错的时候需要根据这个名字找到对应的人来修）
        self.introduction = """
                                👻gbz
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
        
        message: str = event.message
       
        
        gui=0
        Gui=["👻","高柏舟","gbz"]
        for item in Gui:
            if item in message:
                gui=1
                break
            num += 1
        if gui==1:  # 正式进入插件运行部分
            group_id = event.group_id
            effected_group: list = self.config.get("effected_group")
            if group_id not in effected_group:
                self.api.groupService.send_group_msg(group_id=group_id, message=f"该功能未在此群{group_id}生效")
                return
            else:
                text = "给高柏舟跪啦"
                audio_id = await self.get_audio_id(text)
                audio_url = f"https://ottohzys.wzq02.top//get/{audio_id}.ogg"
                print(Record(file=audio_url))
                self.api.groupService.send_group_msg(group_id=group_id, message=f"{Record(file=audio_url)}")

        return

    @classmethod
    async def get_audio_id(cls, text):
        url = "https://ottohzys.wzq02.top//make"
        data = {
            "text": text,
            "inYsddMode": "true",
            "norm": "true",
            "reverse": "false",
            "speedMult": 1,
            "pitchMult": 1
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as res:
                result = await res.json()
                return result.get("id")
