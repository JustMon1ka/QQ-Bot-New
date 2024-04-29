import asyncio
import logging
from multiprocessing import set_start_method


from Bot.Bot import Bot


async def main():
    config_file = "BotConfig.ini"

    bot = Bot(
        config_file=config_file,
    )
    await bot.initialize()
    bot.run()

asyncio.run(main())