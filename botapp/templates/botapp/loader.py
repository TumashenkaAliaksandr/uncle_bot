# botapp/templates/botapp/loader.py
from aiogram import Bot, Dispatcher
from botapp.templates.botapp.config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()
