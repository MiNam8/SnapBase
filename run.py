from aiogram import Bot, Dispatcher
from config import TOKEN
import asyncio
from src.handlers import textbooks, chapters, problems, solutions, menu
from config import configure_logging
import logging

async def main():
    configure_logging(level=logging.INFO)

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # Include your routers
    dp.include_router(textbooks.router)
    dp.include_router(chapters.router)
    dp.include_router(problems.router)
    dp.include_router(solutions.router)
    dp.include_router(menu.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
