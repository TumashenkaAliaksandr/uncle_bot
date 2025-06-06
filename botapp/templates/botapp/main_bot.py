import os
import django
import asyncio
from aiogram import Bot, Dispatcher
from botapp.templates.botapp.config import TOKEN, logger

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uncle_bot.settings')
django.setup()

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Импорт роутеров
from botapp.templates.botapp.handlers import commands, callbacks

# Подключаем роутеры
dp.include_router(commands.router)
dp.include_router(callbacks.router)

async def main():
    logger.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
