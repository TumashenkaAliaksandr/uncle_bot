import os
import django
import asyncio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uncle_bot.settings')
django.setup()

from botapp.templates.botapp.loader import bot, dp
from botapp.templates.botapp.handlers import commands, callbacks

dp.include_router(commands.router)
dp.include_router(callbacks.router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
