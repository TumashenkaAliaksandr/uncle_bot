import os
import asyncio
from aiogram import Router, types
from aiogram.types.input_file import FSInputFile
from aiogram.types import InputMediaAudio, InputMediaPhoto
from asgiref.sync import sync_to_async
from botapp.models import Album
from botapp.bot.config import logger
from botapp.bot.handlers.clear_chat import clear_chat
from botapp.bot.keyboards import settings_keyboard, keyboard, donate_keyboard, get_songs_keyboard
from botapp.bot.texts.proposal_texts import DONATE_TEXT, cleaning_chat_txt, your_settings_txt, \
    MAIN_MENU_ANSWER, nice_listening
from botapp.bot.utils.message_utils import send_and_store
from botapp.bot.loader import sent_messages, bot


router = Router()
MAX_MEDIA_PER_MSG = 10

@router.callback_query(lambda c: c.data and c.data.startswith('album_'))
async def process_album_callback(callback_query: types.CallbackQuery):
    # Отвечаем сразу, чтобы избежать ошибки "query is too old"
    await callback_query.answer()

    album_id = int(callback_query.data.split('_')[1])
    album = await sync_to_async(lambda: Album.objects.filter(id=album_id).first())()
    if not album:
        await send_and_store(callback_query.message.chat.id, "🤷‍♂️ 📀 Альбом не найден.")
        return

    tracks = await sync_to_async(list)(album.tracks.order_by('id').all())
    if not tracks:
        await send_and_store(callback_query.message.chat.id, "🚫 В этом альбоме пока нет треков.")
        return

    photos = []
    audios = []

    # Добавляем обложку в фото, если есть
    if album.cover and album.cover.name:
        cover_path = album.cover.path
        if os.path.isfile(cover_path):
            photos.append(
                InputMediaPhoto(
                    media=FSInputFile(cover_path),
                    caption=(
                        f"📀 Альбом:\n✪ {album.name} ✪\n\n"
                        f"✍️ Описание:\n{album.description}\n\n"
                        f"📅 Релиз: {album.release_date}\n"
                        f"🦸🧙 Авторы: {album.authors}"
                    )
                )
            )
        else:
            await send_and_store(
                callback_query.message.chat.id,
                f"📀 Открываю Альбом:\n ⭐ {album.name} ⭐\n🖼️❌ Обложка не найдена по пути: {cover_path}"
            )
    else:
        await send_and_store(callback_query.message.chat.id, f"📀 Альбом: {album.name}\n🖼️❌ Обложка отсутствует")

    # Добавляем аудио треки
    for track in tracks:
        if track.audio_file and os.path.exists(track.audio_file.path):
            audios.append(
                InputMediaAudio(
                    caption=track.title,
                    media=FSInputFile(track.audio_file.path)
                )
            )
        else:
            logger.warning(f"❌🎵 Аудиофайл не найден или отсутствует: {track.title}")

    # Отправляем фото группами и сохраняем ID сообщений
    if photos:
        for i in range(0, len(photos), MAX_MEDIA_PER_MSG):
            chunk = photos[i:i + MAX_MEDIA_PER_MSG]
            messages = await bot.send_media_group(callback_query.message.chat.id, media=chunk)
            for msg in messages:
                sent_messages.setdefault(callback_query.message.chat.id, []).append(msg.message_id)

    # Отправляем аудио группами с protect_content=True и сохраняем ID сообщений
    if audios:
        for i in range(0, len(audios), MAX_MEDIA_PER_MSG):
            chunk = audios[i:i + MAX_MEDIA_PER_MSG]
            messages = await bot.send_media_group(
                callback_query.message.chat.id,
                media=chunk,
                protect_content=True  # Запрет пересылки аудио
            )
            for msg in messages:
                sent_messages.setdefault(callback_query.message.chat.id, []).append(msg.message_id)

    # Отправляем сообщение с главным меню и сохраняем ID
    await send_and_store(callback_query.message.chat.id, nice_listening, parse_mode="HTML", reply_markup=keyboard)

@router.message(lambda message: message.text == "🎧 Слушать веб версию")
async def show_settings(message: types.Message):
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    # Текст с HTML-ссылкой
    sing_answer_txt = (
        'Вы можете слушать веб-версию по ссылке: '
        '<a href="https://phoenixpegasus.pythonanywhere.com/" target="_blank">Открыть сайт</a>'
    )
    await send_and_store(
        message.chat.id,
        sing_answer_txt,
        parse_mode="HTML",
        reply_markup=keyboard
    )


@router.message(lambda message: message.text == "⚙️")
async def show_settings(message: types.Message):
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    await send_and_store(message.chat.id, your_settings_txt, parse_mode="HTML", reply_markup=settings_keyboard)


@router.message(lambda message: message.text == "🧹 Почистить чат")
async def clear_chat_handler(message: types.Message):
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    await send_and_store(message.chat.id, cleaning_chat_txt, parse_mode="HTML")

    async def clear_and_send_menu():
        await clear_chat(message.chat.id)
        await send_and_store(message.chat.id, MAIN_MENU_ANSWER, parse_mode="HTML", reply_markup=keyboard)

    asyncio.create_task(clear_and_send_menu())


@router.message(lambda message: message.text == "⬅️ Назад")
async def back_to_main_menu(message: types.Message):
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    await send_and_store(message.chat.id, MAIN_MENU_ANSWER, parse_mode="HTML", reply_markup=keyboard)

@router.message(lambda message: message.text == "⬅️")
async def back_to_main_menu(message: types.Message):
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    await send_and_store(message.chat.id, MAIN_MENU_ANSWER, parse_mode="HTML", reply_markup=keyboard)


@router.message(lambda message: message.text == "💰 Донаты")
async def donate_handler(message: types.Message):
    # Сохраняем ID входящего сообщения пользователя для удаления
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    await send_and_store(
        message.chat.id,
        DONATE_TEXT,
        reply_markup=donate_keyboard,
        parse_mode="HTML"
    )


@router.message(lambda message: message.text == "🎸 Табы")
async def tab_handler(message: types.Message):
    keyboard = await get_songs_keyboard()
    await message.answer("✅ Выберите песню что бы получить текст и аккорды:", reply_markup=keyboard)


@router.message(lambda message: message.text == "📺 Видео")
async def video_handler(message: types.Message):
    await message.answer("🤷‍♂ Сорян, видосов пока нет..")


@router.message(lambda message: message.text == "📰 Новости")
async def news_handler(message: types.Message):
    await message.answer("🤷‍♂ Сорян, Новостей пока нет..")

