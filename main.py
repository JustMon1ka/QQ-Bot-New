import asyncio

from Bot.Bot import Bot


async def main():
    server_address = "120.26.217.8:5700"
    client_address = "127.0.0.1:7000"

    bot = Bot(server_address, client_address, True)
    await bot.initialize()
    bot.run()

asyncio.run(main())