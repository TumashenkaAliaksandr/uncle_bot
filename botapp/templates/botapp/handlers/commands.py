from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from botapp.templates.botapp.keyboards import keyboard, albums_keyboard, donate_keyboard
from botapp.templates.botapp.config import logger
from botapp.templates.botapp.texts.proposal_texts import thanks_donate_command_txt, HELLO_TXT_FIRST, sending_album_txt
from botapp.templates.botapp.utils.message_utils import send_and_store
from botapp.templates.botapp.loader import sent_messages

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    logger.info(f"Пользователь {message.from_user.id} запустил /start")
    await send_and_store(
        message.chat.id,
        HELLO_TXT_FIRST,
        parse_mode="HTML",
        reply_markup=keyboard
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    logger.info(f"👤 Пользователь {message.from_user.id} запросил /help")
    await send_and_store(
        message.chat.id,
        "♻️ Доступные команды:\n"
        "/start — приветствие\n"
        "/help — помощь\n"
        "/music — музыка\n"
        "/donate — донаты"
    )

@router.message(F.text.in_({"/music", "🎵 Музыка"}))
async def cmd_music(message: Message):
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    logger.info(f"👤 Пользователь {message.from_user.id} запросил /music или нажал кнопку Музыка")
    markup = await albums_keyboard()
    await send_and_store(message.chat.id, sending_album_txt, parse_mode="HTML", reply_markup=markup)

@router.message(Command("donate"))
async def cmd_donate(message: Message):
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    logger.info(f"👤 Пользователь {message.from_user.id} запросил /donate")
    await send_and_store(
        message.chat.id, thanks_donate_command_txt, parse_mode="HTML", reply_markup=donate_keyboard,
    )
