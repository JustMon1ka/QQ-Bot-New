import aiohttp
import asyncio


class Api:
    def __init__(self, server_address):
        self.bot_api_address = f"http://{server_address}/"

        # 传递Api类的实例引用
        self.botSelfInfo = self.BotSelfInfo(self)
        self.privateService = self.PrivateService(self)

    class BotSelfInfo:
        def __init__(self, api_instance):
            self.api = api_instance  # 保存对Api类实例的引用

        async def get_login_info(self):
            """
            获取bot本身的登录信息，用来检查bot对象是否初始化成功
            :return: bot的登录信息
            """
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api.bot_api_address) as res:
                    return await res.text()

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