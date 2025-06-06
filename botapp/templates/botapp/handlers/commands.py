from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from botapp.templates.botapp.keyboards import keyboard, albums_keyboard
from botapp.templates.botapp.config import logger

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    logger.info(f"Пользователь {message.from_user.id} запустил /start")
    await message.answer(
        "Привет! 👋😊\nЯ музыкальный Дядябот 🎵\n"
        "Я помогу тебе слушать треки группы ДядЯ.\n"
        "Выбери опцию ниже или используй кнопки под полем ввода.",
        reply_markup=keyboard
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    logger.info(f"Пользователь {message.from_user.id} запросил /help")
    await message.answer(
        "Доступные команды:\n"
        "/start — приветствие\n"
        "/help — помощь\n"
        "/music — музыка\n"
        "/donate — донаты"
    )

@router.message(F.text.in_({"/music", "🎵 Музыка"}))
async def cmd_music(message: Message):
    logger.info(f"Пользователь {message.from_user.id} запросил /music или нажал кнопку Музыка")
    markup = await albums_keyboard()
    await message.answer("Выберите альбом:", reply_markup=markup)

@router.message(Command("donate"))
async def cmd_donate(message: Message):
    logger.info(f"Пользователь {message.from_user.id} запросил /donate")
    await message.answer(
        "💰 Раздел Донаты:\n"
        "Спасибо за поддержку! Вот информация, как можно сделать донат."
    )
