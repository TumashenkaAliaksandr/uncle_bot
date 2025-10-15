import logging
import os
import asyncio
from aiogram import Router, types
from aiogram.exceptions import TelegramEntityTooLarge
from aiogram.types.input_file import FSInputFile
from aiogram.types import InputMediaAudio, InputMediaPhoto
from asgiref.sync import sync_to_async
from botapp.models import Album
from botapp.bot.config import logger
from botapp.bot.keyboards import keyboard
from botapp.bot.texts.proposal_texts import nice_listening
from botapp.bot.utils.message_utils import send_and_store
from botapp.bot.loader import sent_messages, bot


logger = logging.getLogger(__name__)
router = Router()
MAX_MEDIA_PER_MSG = 5  # Максимум элементов в одной медиагруппе
sent_messages = {}  # Словарь для хранения ID отправленных сообщений
nice_listening = "Приятного прослушивания!"  # Сообщение после альбома
keyboard = keyboard  # Подставьте сюда вашу главную клавиатуру



# Безопасная отправка медиагрупп с разбиением на части и обработкой ошибок
async def safe_send_media_group(bot, chat_id, media_chunks, **kwargs):
    for chunk in media_chunks:
        try:
            messages = await bot.send_media_group(chat_id=chat_id, media=chunk, **kwargs)
            for msg in messages:
                sent_messages.setdefault(chat_id, []).append(msg.message_id)
        except TelegramEntityTooLarge:
            # Если чанк слишком большой, отправляем по одному элементу
            for media in chunk:
                try:
                    single_msg = await bot.send_media_group(chat_id=chat_id, media=[media], **kwargs)
                    sent_messages.setdefault(chat_id, []).append(single_msg[0].message_id)
                except Exception as e:
                    logger.error(f"Ошибка при отправке медиа: {e}")
        await asyncio.sleep(1)  # Пауза между чанками


@router.callback_query(lambda c: c.data and c.data.startswith('album_'))
async def process_album_callback(callback_query: types.CallbackQuery):
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

    # Добавление обложки
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

    # Добавление аудио треков
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

    # Разбиение на чанки
    photo_chunks = [photos[i:i + MAX_MEDIA_PER_MSG] for i in range(0, len(photos), MAX_MEDIA_PER_MSG)]
    audio_chunks = [audios[i:i + MAX_MEDIA_PER_MSG] for i in range(0, len(audios), MAX_MEDIA_PER_MSG)]

    # Отправляем фото чанками
    if photos:
        await safe_send_media_group(bot, callback_query.message.chat.id, photo_chunks)

    # Отправляем аудио чанками с защитой содержимого
    if audios:
        await safe_send_media_group(bot, callback_query.message.chat.id, audio_chunks, protect_content=True)

    # Отправляем сообщение с клавиатурой
    await send_and_store(callback_query.message.chat.id, nice_listening, parse_mode="HTML", reply_markup=keyboard)






