from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from botapp.models import Album
from asgiref.sync import sync_to_async
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from botapp.models import SongInfo

# Главная клавиатура с тремя кнопками: Музыка, Донаты, Настройки
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎵 Музыка"), KeyboardButton(text="📰 Новости"), KeyboardButton(text="📣 Канал")],
        [KeyboardButton(text="🧬 Платформы"), KeyboardButton(text="📺 Видео"), KeyboardButton(text="💰 Донаты")],
        [KeyboardButton(text="🎸 Табы"), KeyboardButton(text="✒️ Написать"), KeyboardButton(text="⚙️")],
    ],
    resize_keyboard=True
)

# Клавиатура настроек с кнопкой "Почистить чат" и "Назад"
settings_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧹 Почистить чат")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

async def albums_keyboard():
    albums = await sync_to_async(list)(Album.objects.all())
    builder = InlineKeyboardBuilder()
    for album in albums:
        builder.button(
            text=f"🎵 {album.name}",
            callback_data=f"album_{album.id}"
        )
    builder.adjust(1)
    return builder.as_markup()


donate_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💎 Поддержать через Tribute", url="https://t.me/tribute_bot?start=yourchannel")],
    [InlineKeyboardButton(text="☁️ CloudTips", url="https://cloudtips.ru/yourprofile")],
    [InlineKeyboardButton(text="💳 ЮKassa", url="https://yookassa.ru/yourpaymentlink")]
])


async def get_songs_keyboard():
    songs = await sync_to_async(list)(SongInfo.objects.all())

    buttons = []
    for song in songs:
        buttons.append([InlineKeyboardButton(text=song.title, callback_data=f"song_{song.id}")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


platforms_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📷 Инстаграмм", url="https://www.instagram.com/dyadya_44/")],
    [InlineKeyboardButton(text="🎥 Ютуб", url="https://www.youtube.com/@juniorpegasus6871")],
    [InlineKeyboardButton(text="🌐 Слушать веб версию", url="http://164.92.218.63/")],
])
