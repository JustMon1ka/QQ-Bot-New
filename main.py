import asyncio

from Bot.Bot import Bot


async def main():
    server_address = "bot.server.address:5700"
    client_address = "127.0.0.1:7000"
    config_file = "BotConfig.ini"

    bot = Bot(
        server_address=server_address,
        client_address=client_address,
        config_file=config_file,
        debug=True
    )
    await bot.initialize()
    bot.run()

asyncio.run(main())