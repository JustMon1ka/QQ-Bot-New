import aiohttp
import asyncio

import requests


class Api:
    def __init__(self, server_address):
        self.bot_api_address = f"http://{server_address}/"

        # 传递Api类的实例引用
        self.botSelfInfo = self.BotSelfInfo(self)
        self.privateService = self.PrivateService(self)
        self.groupService = self.GroupService(self)

    class BotSelfInfo:
        def __init__(self, api_instance):
            self.api = api_instance  # 保存对Api类实例的引用

        async def get_login(self):
            """
            获取bot服务端是否在线
            :return: bot服务端返回的信息
            """
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api.bot_api_address) as res:
                    return await res.text()

        def get_login_info(self):
            """
            获取bot自身的登录信息
            :return: bot的QQ号和昵称
            """
            res = requests.get(self.api.bot_api_address + "get_login_info")
            return res.json()

    class PrivateService:
        def __init__(self, api_instance):
            self.api = api_instance  # 保存对Api类实例的引用

        async def send_private_msg(self, user_id, message):
            params = {
                "user_id": user_id,
                "message": message
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api.bot_api_address + "send_private_msg", params=params) as res:
                    return await res.json()

    class GroupService:
        def __init__(self, api_instance):
            self.api = api_instance  # 保存对Api类实例的引用

        async def get_group_member_list(self, group_id):
            params = {
                "group_id": group_id
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api.bot_api_address + "get_group_member_list", params=params) as res:
                    return await res.json()

        async def send_group_msg(self, group_id, message):
            params = {
                "group_id": group_id,
                "message": message
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api.bot_api_address + "send_group_msg", params=params) as res:
                    return await res.json()