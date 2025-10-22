import logging
import os
import asyncio
from datetime import datetime, timezone

from aiogram import Router, types
from aiogram.exceptions import TelegramEntityTooLarge
from aiogram.types.input_file import FSInputFile
from aiogram.types import InputMediaAudio, InputMediaPhoto, CallbackQuery
from asgiref.sync import sync_to_async
from django.templatetags.tz import utc
from django.utils.timezone import make_aware, get_current_timezone

from botapp.models import Album, News, SongInfo
from botapp.bot.config import logger
from botapp.bot.keyboards import main_keyboard, news_keyboard, get_see_keyboard
from botapp.bot.texts.proposal_texts import nice_listening
from botapp.bot.utils.message_utils import send_and_store
from botapp.bot.loader import sent_messages, bot


logger = logging.getLogger(__name__)
router = Router()
MAX_MEDIA_PER_MSG = 5  # Максимум элементов в одной медиагруппе
nice_listening = "Приятного прослушивания!"  # Сообщение после альбома
keyboard = main_keyboard  # Подставьте сюда вашу главную клавиатуру



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


@router.callback_query(lambda c: c.data == "news_today")
async def news_today_handler(callback: CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id

    today = datetime.now().date()
    news_qs = await sync_to_async(lambda: list(
        News.objects.filter(date__date=today).select_related('track').order_by('-date')
    ))()

    if not news_qs:
        sent_msg = await callback.message.answer("💡 Сегодня новостей пока нет.")
        sent_messages.setdefault(chat_id, []).append(sent_msg.message_id)
        return

    for news_item in news_qs:
        date_str = news_item.date.strftime('%d.%m.%Y %H:%M')
        text = (
            f"<b>{news_item.title_news}</b>\n"
            f"📅 Дата: {date_str}\n"
        )
        if news_item.track:
            text += f"🎼 Трек: <b>{news_item.track.title}</b>\n"

        keyboard = get_see_keyboard(news_item.id)
        sent_msg = await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
        sent_messages.setdefault(chat_id, []).append(sent_msg.message_id)


@router.callback_query(lambda c: c.data == "news_old")
async def news_all_handler(callback: CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id

    news_qs = await sync_to_async(lambda: list(
        News.objects.select_related('track').order_by('-date')
    ))()

    if not news_qs:
        sent_msg = await callback.message.answer("💡 Новости не найдены.")
        sent_messages.setdefault(chat_id, []).append(sent_msg.message_id)
        return

    for news_item in news_qs:
        date_str = news_item.date.strftime('%d.%m.%Y %H:%M')
        text = (
            f"<b>{news_item.title_news}</b>\n"
            f"📅 Дата: {date_str}\n"
        )
        if news_item.track:
            text += f"🎼 Трек: <b>{news_item.track.title}</b>\n"

        keyboard = get_see_keyboard(news_item.id)
        sent_msg = await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
        sent_messages.setdefault(chat_id, []).append(sent_msg.message_id)


@router.callback_query(lambda c: c.data and c.data.startswith("show_news_"))
async def show_news_handler(callback: CallbackQuery):
    await callback.answer()
    news_id = int(callback.data[len("show_news_"):])
    news_item = await sync_to_async(
        lambda: News.objects.filter(id=news_id).select_related('track').first()
    )()

    if not news_item:
        await callback.message.answer("❌ Новость не найдена.")
        return

    text = f"<b>{news_item.title_news}</b>\n\n{news_item.description}"
    if news_item.track:
        text += f"\n\n🎼 <b>Трек:</b> {news_item.track.title}"
        if news_item.track.description:
            text += f"\n\n📝 <b>Описание:</b>\n{news_item.track.description}"

    # Отправляем фото, если есть
    if news_item.photo and news_item.photo.path and os.path.isfile(news_item.photo.path):
        sent_photo = await callback.message.answer_photo(
            photo=FSInputFile(news_item.photo.path),
            caption=text,
            parse_mode="HTML"
        )
        sent_messages.setdefault(callback.message.chat.id, []).append(sent_photo.message_id)
    else:
        sent_msg = await callback.message.answer(text, parse_mode="HTML")
        sent_messages.setdefault(callback.message.chat.id, []).append(sent_msg.message_id)

    # Отправляем аудио, если есть и файл существует
    if news_item.track:
        audio_path = news_item.track.audio_file.path if news_item.track.audio_file else None
        if audio_path and os.path.isfile(audio_path):
            sent_audio = await callback.message.answer_audio(
                audio=FSInputFile(audio_path),
                caption=news_item.track.title
            )
            sent_messages[callback.message.chat.id].append(sent_audio.message_id)


# Обработчик для нажатия на "посмотреть" песню
@router.callback_query(lambda c: c.data and c.data.startswith("song_"))
async def show_song_handler(callback: CallbackQuery):
    await callback.answer()
    song_id = int(callback.data[len("song_"):])
    song = await sync_to_async(lambda: SongInfo.objects.filter(id=song_id).first())()

    if not song:
        await callback.message.answer("🎵 Песня не найдена.")
        return

    text = f"<b>Песня: {song.title}</b>\n\n🎧💌📖\n<b>Текст:</b>\n────୨ৎ────\n{song.lyrics}\n\n𝄞⨾𓍢⭐໋🎸⋆⭒˚｡⋆ \n<b>Аккорды:</b>\n────୨ৎ────\n{song.chords}"

    sent_msg = await callback.message.answer(text, parse_mode="HTML")
    sent_messages.setdefault(callback.message.chat.id, []).append(sent_msg.message_id)
