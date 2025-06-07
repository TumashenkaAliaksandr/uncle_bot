# botapp/templates/botapp/main_bot.py
import os
import django
import asyncio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uncle_bot.settings')
django.setup()

from botapp.templates.botapp.loader import bot, dp
from botapp.templates.botapp.handlers import commands, callbacks
from botapp.templates.botapp.handlers.proposal_handlers import router as proposal_router  # корректный импорт

dp.include_router(commands.router)
dp.include_router(callbacks.router)
dp.include_router(proposal_router)

async def main():
    from botapp.templates.botapp.config import logger
    logger.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
