import asyncio

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from botapp.bot.handlers.clear_chat import clear_chat
from botapp.bot.keyboards import keyboard, albums_keyboard, donate_keyboard, settings_keyboard, get_songs_keyboard, \
    platforms_keyboard
from botapp.bot.config import logger
from botapp.bot.texts.proposal_texts import thanks_donate_command_txt, HELLO_TXT_FIRST, sending_album_txt, \
    YOUR_SETTINGS_TXT, news_txt, DONATE_TEXT, tabs_txt, MAIN_MENU_ANSWER, cleaning_chat_txt
from botapp.bot.utils.message_utils import send_and_store
from botapp.bot.loader import sent_messages

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



@router.message(lambda message: message.text == "⚙️")
async def show_settings(message: Message):
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    logger.info(f"👤 Пользователь {message.from_user.id} запросил /settings")
    await send_and_store(
        message.chat.id, YOUR_SETTINGS_TXT, parse_mode="HTML", reply_markup=settings_keyboard,
    )

@router.message(lambda message: message.text == "📺 Видео")
async def video_handler(message: Message):
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    await send_and_store(message.chat.id,"🤷‍♂ Сорян, видосов пока нет..")


@router.message(lambda message: message.text == "📰 Новости")
async def news_handler(message: Message):
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    logger.info(f"👤 Пользователь {message.from_user.id} запросил /news")
    await send_and_store(
        message.chat.id, news_txt, parse_mode="HTML"
    )

@router.message(lambda message: message.text == "💰 Донаты")
async def donate_handler(message: Message):
    # Сохраняем ID входящего сообщения пользователя для удаления
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    await send_and_store(
        message.chat.id,
        DONATE_TEXT,
        reply_markup=donate_keyboard,
        parse_mode="HTML"
    )



@router.message(lambda message: message.text == "🎸 Табы")
async def tab_handler(message: Message):
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    keyboard = await get_songs_keyboard()
    await send_and_store(message.chat.id, tabs_txt, parse_mode="HTML", reply_markup=keyboard)

@router.message(lambda message: message.text == "⬅️ Назад")
async def back_to_main_menu(message: Message):
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    await send_and_store(message.chat.id, MAIN_MENU_ANSWER, parse_mode="HTML", reply_markup=keyboard)

@router.message(lambda message: message.text == "⬅️")
async def back_to_main_menu(message: Message):
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    await send_and_store(message.chat.id, MAIN_MENU_ANSWER, parse_mode="HTML", reply_markup=keyboard)

@router.message(lambda message: message.text == "🧹 Почистить чат")
async def clear_chat_handler(message: Message):
    logger.info(f"👤 Пользователь {message.from_user.id} запросил 🧹 Почистить чат")
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    await send_and_store(message.chat.id, cleaning_chat_txt, parse_mode="HTML")

    async def clear_and_send_menu():
        logger.info(f"БОТ {message.from_user.id} 🧹 Чистит чат")
        await clear_chat(message.chat.id)
        await send_and_store(message.chat.id, MAIN_MENU_ANSWER, parse_mode="HTML", reply_markup=keyboard)

    asyncio.create_task(clear_and_send_menu())


@router.message(lambda message: message.text == "🧬 Платформы")
async def show_settings(message: Message):
    # Сохраняем ID входящего сообщения пользователя для удаления
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    await send_and_store(
        message.chat.id,
        DONATE_TEXT,
        reply_markup=platforms_keyboard,
        parse_mode="HTML"
    )


@router.message(lambda message: message.text == "📣 Канал")
async def show_settings(message: Message):
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    # Текст с HTML-ссылкой
    sing_answer_txt = (
        '<strong>Перейти в телеграмм канал ДЯДЯ?</strong> 🚶 ˋ°•*⁀➷'
        '<a href="https://t.me/+M-LokUWMIaBmYTFi" target="_blank">Перейти в канaл</a>'
    )
    await send_and_store(
        message.chat.id,
        sing_answer_txt,
        parse_mode="HTML",
        reply_markup=keyboard
    )
