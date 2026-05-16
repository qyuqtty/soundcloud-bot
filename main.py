import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from handlers import router


async def main():
    if not BOT_TOKEN:
        print("(╥﹏╥) Ошибка: BOT_TOKEN не найден в .env файле!")
        return

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()
    dp.include_router(router)

    print("(◕‿◕) Бот успешно запущен")
    print("(¬_¬) Ожидаю вашу ссылку...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())