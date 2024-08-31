import aiohttp
import re
import requests

from bs4 import BeautifulSoup
from CQMessage.CQType import Image
from Plugins import Plugins
from Event.EventHandler import GroupMessageEventHandler

headers ={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0"
}
class Wallpaper(Plugins):
    """
    这是一个插件的模板，开发一个新的插件至少应该包含以下部分
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "Wallpaper"  # 插件的名字（一定要和类的名字完全一致（主要是我能力有限，否则会报错））
        self.type = "Group"  # 插件的类型（这个插件是在哪种消息类型中触发的）
        self.author = "Yuyu"  # 插件开发作者（不用留真名，但是当插件报错的时候需要根据这个名字找到对应的人来修）
        self.introduction = """
                                Wallpaper
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
                self.api.groupService.send_group_msg(group_id=group_id, message=f"该功能未在此群{group_id}生效")
                return
            elif len_of_command < 3:
                self.api.groupService.send_group_msg(group_id=group_id, message="Voicemaker插件用法：<bot> voice "
                                                                                      "<text>。缺少参数<text>")
                return
            else:
                text = command_list[2]
                num = 1
                if len_of_command == 4:
                    if int(command_list[3])>=1:
                        num = int(command_list[3])
                audio_url = await self.get_audio_id(text)
                if audio_url=="none":
                    self.api.groupService.send_group_msg(group_id=group_id, message="无相关图片")
                    return
                response = requests.get(audio_url,headers=headers)
                html=response.text
                soup=BeautifulSoup(html,"html.parser") 
                all_imgs=soup.findAll("img")
                number=0
                for img in all_imgs:
                    alt=img["alt"]
                    if text in alt:
                        src=img["data-original"]
                        print(Image(file=src))
                        self.api.groupService.send_group_msg(group_id=group_id, message=f"{Image(file=src)}")
                        number +=1
                        if number>=num:
                            return

        return

    @classmethod
    async def get_audio_id(cls, text):
        url = "https://www.moyublog.com/e/search/index.php"
        data = {
            "keyboard": text,
            "show": "title",
            "tempid": "8",
            "classid": "95"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as res:
                html = await res.text()
                pattern = r'<meta\s+property="og:url"\s+content="([^"]+)"'  
                match = re.search(pattern, html)  
                if match:
                    return  match.group(1)  
                else:
                    return "none"
