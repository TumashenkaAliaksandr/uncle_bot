# bot/templates/bot/loader.py
import logging
from aiogram import Bot, Dispatcher
from botapp.bot.config import TOKEN
from botapp.bot.handlers.morder import register_moderation_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Регистрируем модерационные обработчики
register_moderation_handlers(dp)

sent_messages = {}
