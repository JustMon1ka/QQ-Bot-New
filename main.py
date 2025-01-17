import asyncio
from Bot.Bot import Bot


async def main():
    config_file = "BotConfig.ini"

    bot = Bot(
        config_file=config_file,
    )
    await bot.initialize()
    bot.runWebCtrler()


asyncio.run(main())
