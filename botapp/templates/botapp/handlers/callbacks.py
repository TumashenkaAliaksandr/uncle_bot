import os
import asyncio
from aiogram import Router, types
from aiogram.types.input_file import FSInputFile
from aiogram.types import InputMediaAudio, InputMediaPhoto
from asgiref.sync import sync_to_async

from botapp.models import Album
from botapp.templates.botapp.config import logger
from botapp.templates.botapp.handlers.clear_chat import clear_chat
from botapp.templates.botapp.keyboards import settings_keyboard, keyboard

router = Router()
MAX_MEDIA_PER_MSG = 10

@router.callback_query(lambda c: c.data and c.data.startswith('album_'))
async def process_album_callback(callback_query: types.CallbackQuery):
    album_id = int(callback_query.data.split('_')[1])
    album = await sync_to_async(lambda: Album.objects.filter(id=album_id).first())()
    if not album:
        await callback_query.message.answer("🤷‍♂️ 📀Альбом не найден.")
        await callback_query.answer()
        return

    tracks = await sync_to_async(list)(album.tracks.order_by('id').all())
    if not tracks:
        await callback_query.message.answer("🚫 В этом альбоме пока нет треков.")
        await callback_query.answer()
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
                    caption=f"📀 Альбом: {album.name}"
                )
            )
        else:
            await callback_query.message.answer(
                f"📀 Открываю Альбом:\n ⭐ {album.name} ⭐\n🖼️ Обложка не найдена по пути: {cover_path}"
            )
    else:
        await callback_query.message.answer(f"📀 Альбом: {album.name}\n🖼️ Обложка отсутствует")

    # Добавляем аудио треки
    for track in tracks:
        if track.audio_file and os.path.exists(track.audio_file.path):
            audios.append(
                InputMediaAudio(
                    media=FSInputFile(track.audio_file.path),
                    caption=track.title
                )
            )
        else:
            logger.warning(f"Аудиофайл не найден или отсутствует: {track.title}")

    # Отправляем фото группами
    if photos:
        for i in range(0, len(photos), MAX_MEDIA_PER_MSG):
            chunk = photos[i:i + MAX_MEDIA_PER_MSG]
            await callback_query.message.answer_media_group(media=chunk)

    # Отправляем аудио группами
    if audios:
        for i in range(0, len(audios), MAX_MEDIA_PER_MSG):
            chunk = audios[i:i + MAX_MEDIA_PER_MSG]
            await callback_query.message.answer_media_group(media=chunk)

    await callback_query.answer()


@router.message(lambda message: message.text == "⚙️ Настройки")
async def show_settings(message: types.Message):
    await message.answer("Вы в настройках:", reply_markup=settings_keyboard)


@router.message(lambda message: message.text == "🧹 Почистить чат")
async def clear_chat_handler(message: types.Message):
    await message.answer("Через 5 минут начнётся очистка чата.")
    asyncio.create_task(clear_chat(message.chat.id))


@router.message(lambda message: message.text == "⬅️ Назад")
async def back_to_main_menu(message: types.Message):
    await message.answer("Главное меню:", reply_markup=keyboard)
