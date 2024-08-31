from io import BytesIO
import random
import aiohttp
import requests

from bs4 import BeautifulSoup
from CQMessage.CQType import Image
from Plugins import Plugins
from Event.EventHandler import GroupMessageEventHandler

headers ={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0"
}
class Image(Plugins):
    """
    这是一个插件的模板，开发一个新的插件至少应该包含以下部分
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "Image"  # 插件的名字（一定要和类的名字完全一致（主要是我能力有限，否则会报错））
        self.type = "Group"  # 插件的类型（这个插件是在哪种消息类型中触发的）
        self.author = "Yuyu"  # 插件开发作者（不用留真名，但是当插件报错的时候需要根据这个名字找到对应的人来修）
        self.introduction = """
                                Image
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
                await self.api.groupService.send_group_msg(group_id=group_id, message=f"该功能未在此群{group_id}生效")
                return
            elif len_of_command < 3:
                await self.api.groupService.send_group_msg(group_id=group_id, message="Voicemaker插件用法：<bot> voice "
                                                                                      "<text>。缺少参数<text>")
                return
            else:
                text = command_list[2]
                num = 1
                if len_of_command == 4:
                    if int(command_list[3])>=1:
                        num = int(command_list[3])
                url = f"https://wallhere.com/zh/wallpapers?q={text}"  
                response = requests.get(url,headers=headers)
                html=response.text
                soup=BeautifulSoup(html,"html.parser")
                all_image=soup.findAll("image")
                number=0
                for img in all_image:
                    alt=img["alt"]
                    if text in alt:
                        src=img["data-src"]
                        print(Image(file=src))
                        await self.api.groupService.send_group_msg(group_id=group_id, message=f"{Image(file=src)}")
                        number +=1
                        if number>=num:
                            return
        return       
                
                        


    # @classmethod
    # async def get_audio_id(cls, text):  
    #     url = f"https://wallhere.com/zh/wallpapers?q={text}"  
    #     response = requests.get(url,allow_redirects=True)
    #     data = {  
    #         "category": 0,  
    #         "categoryId": 0,  
    #         "color": 0, 
    #         "current": 1,  
    #         "keyword": text,  
    #         "ratio": 0,  
    #         "resolution": 3,  
    #         "size": 24,  
    #         "sort": 1  
    #     }  
    #     async with aiohttp.ClientSession() as session:  
    #         async with session.post(url, json=data) as res:  
    #             if res.status == 200:  
    #                 response = await res.json()  
    #                 if 'data' in response and 'list' in response['data']:  
       
    #                     items = response['data']['list']  
    #                     if len(items) >= 5:  
    #                         random_index = random.randint(0, 4)  
    #                         return items[random_index]['i']  
    #                     else:  
    #                         if items:  
    #                             random_index = random.randint(0, len(items) - 1)  
    #                             return items[random_index]['i']  
    #                         else:  
    #                             return None  # 或者 raise ValueError("List is empty")  
    #                 else:  
    #                     return None  # 或者 raise ValueError("Invalid response format")  
