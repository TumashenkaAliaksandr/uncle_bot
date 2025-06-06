from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from botapp.models import Album
from asgiref.sync import sync_to_async

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎵 Музыка"), KeyboardButton(text="💰 Донаты")]
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
