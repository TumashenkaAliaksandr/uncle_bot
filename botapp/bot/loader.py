# bot/templates/bot/loader.py
from aiogram import Bot, Dispatcher
from botapp.bot.config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

sent_messages = {}
