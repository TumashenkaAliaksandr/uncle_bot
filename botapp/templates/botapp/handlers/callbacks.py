import os
from aiogram import Router, types
from aiogram.types.input_file import FSInputFile
from aiogram.types import InputMediaAudio, InputMediaPhoto
from asgiref.sync import sync_to_async

from botapp.models import Album
from botapp.templates.botapp.config import logger
from django.conf import settings

router = Router()
MAX_MEDIA_PER_MSG = 10

@router.callback_query(lambda c: c.data and c.data.startswith('album_'))
async def process_album_callback(callback_query: types.CallbackQuery):
    album_id = int(callback_query.data.split('_')[1])
    album = await Album.objects.filter(id=album_id).afirst()
    if not album:
        await callback_query.message.answer("🤷‍♂️ 📀Альбом не найден.")
        await callback_query.answer()
        return

    tracks = await sync_to_async(list)(album.tracks.order_by('id').all())
    if not tracks:
        await callback_query.message.answer("🚫 В этом альбоме пока нет треков.")
        await callback_query.answer()
        return

    media = []

    if album.cover and album.cover.name:
        cover_path = album.cover.path
        if os.path.isfile(cover_path):
            media.append(
                InputMediaPhoto(
                    media=FSInputFile(cover_path),
                    caption=f"📀 Альбом: {album.name}"
                )
            )
        else:
            await callback_query.message.answer(f"📀 Открываю Альбом:\n ⭐ {album.name} ⭐\n🖼️ Обложка не найдена по пути: {cover_path}")
    else:
        await callback_query.message.answer(f"📀 Альбом: {album.name}\n🖼️ Обложка отсутствует")

    for track in tracks:
        if track.audio_file and os.path.exists(track.audio_file.path):
            media.append(
                InputMediaAudio(
                    media=FSInputFile(track.audio_file.path),
                    caption=track.title
                )
            )
        else:
            logger.warning(f"Аудиофайл не найден или отсутствует: {track.title}")

    for i in range(0, len(media), MAX_MEDIA_PER_MSG):
        chunk = media[i:i + MAX_MEDIA_PER_MSG]
        await callback_query.message.answer_media_group(media=chunk)

    await callback_query.answer()
