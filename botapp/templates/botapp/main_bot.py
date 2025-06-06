import io
import logging
import asyncio
import os

import django
from aiogram.types.input_file import FSInputFile
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.types import InputMediaAudio, InputMediaPhoto
from asgiref.sync import sync_to_async
from django.conf import settings

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uncle_bot.settings')
django.setup()

from botapp.models import Album, Track  # импорт моделей

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

TOKEN = "1689625811:AAHJ9ZRqy-oiPvI43d68HdWLc1awBj_T2I8"  # Замените на токен своего бота

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Reply клавиатура с эмодзи
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎵 Музыка"), KeyboardButton(text="💰 Донаты")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} запустил /start")
    await message.answer(
        "Привет! 👋😊\nЯ музыкальный Дядябот 🎵\n"
        "Я помогу тебе слушать треки группы ДядЯ.\n"
        "Выбери опцию ниже или используй кнопки под полем ввода.",
        reply_markup=keyboard
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} запросил /help")
    await message.answer(
        "Доступные команды:\n"
        "/start — приветствие\n"
        "/help — помощь\n"
        "/music — музыка\n"
        "/donate — донаты"
    )

@dp.message(lambda message: message.text in ["/music", "🎵 Музыка"])
async def cmd_music(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} запросил /music или нажал кнопку Музыка")

    albums = await sync_to_async(list)(Album.objects.all())
    if not albums:
        await message.answer("Пока нет доступных альбомов.")
        return

    builder = InlineKeyboardBuilder()
    for album in albums:
        builder.button(
            text=f"🎵 {album.name}",
            callback_data=f"album_{album.id}"
        )
    builder.adjust(1)

    await message.answer("Выберите альбом:", reply_markup=builder.as_markup())

@dp.callback_query(lambda c: c.data and c.data.startswith('album_'))
async def process_album_callback(callback_query: types.CallbackQuery):
    album_id = int(callback_query.data.split('_')[1])
    album = await sync_to_async(Album.objects.filter(id=album_id).first)()
    if not album:
        await callback_query.message.answer("Альбом не найден.")
        await callback_query.answer()
        return

    tracks = await sync_to_async(list)(album.tracks.order_by('id').all())
    if not tracks:
        await callback_query.message.answer("В этом альбоме пока нет треков.")
        await callback_query.answer()
        return

    media = []

    # Правильное получение пути к обложке
    if album.cover and album.cover.name:
        cover_path = album.cover.path  # <-- здесь важно использовать .path, а не .url
        if os.path.isfile(cover_path):
            media.append(
                InputMediaPhoto(
                    media=FSInputFile(cover_path),
                    caption=f"Гружу Альбом: {album.name}",
                    # has_spoiler=True  # можно раскомментировать для обхода кеша
                )
            )
        else:
            await callback_query.message.answer(f"Альбом: {album.name}\nОбложка не найдена по пути: {cover_path}")
    else:
        await callback_query.message.answer(f"Альбом: {album.name}\nОбложка отсутствует")

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

    MAX_MEDIA_PER_MSG = 10
    for i in range(0, len(media), MAX_MEDIA_PER_MSG):
        chunk = media[i:i + MAX_MEDIA_PER_MSG]
        await callback_query.message.answer_media_group(media=chunk)

    await callback_query.answer()

@dp.callback_query(lambda c: c.data == "back_to_albums")
async def back_to_albums(callback_query: types.CallbackQuery):
    albums = await sync_to_async(list)(Album.objects.all())
    builder = InlineKeyboardBuilder()
    for album in albums:
        builder.button(
            text=f"🎵 {album.name}",
            callback_data=f"album_{album.id}"
        )
    builder.adjust(1)

    await callback_query.message.edit_text("Альбом:", reply_markup=builder.as_markup())
    await callback_query.answer()

@dp.message(Command("donate"))
async def cmd_donate(message: types.Message):
    logger.info(f"Пользователь {message.from_user.id} запросил /donate")
    await message.answer(
        "💰 Раздел Донаты:\n"
        "Спасибо за поддержку! Вот информация, как можно сделать донат."
    )

@dp.message()
async def log_user_info(message: types.Message):
    user = message.from_user
    user_id = user.id
    username = user.username or "нет никнейма"
    logger.info(f"Пользователь ID: {user_id}, Никнейм: @{username}")

async def main():
    logger.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
