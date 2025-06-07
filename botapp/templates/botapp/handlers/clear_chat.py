import asyncio

from botapp.templates.botapp.keyboards import keyboard
from botapp.templates.botapp.loader import bot, sent_messages
from botapp.templates.botapp.config import logger

async def clear_chat(chat_id: int, delay_seconds: int = 5):
    await asyncio.sleep(delay_seconds)
    logger.info(f"Начинаю очистку чата {chat_id}")

    message_ids = sent_messages.get(chat_id, [])
    for message_id in message_ids:
        try:
            await bot.delete_message(chat_id, message_id)
            logger.info(f"Удалено сообщение {message_id} в чате {chat_id}")
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение {message_id}: {e}")

    sent_messages[chat_id] = []
    logger.info(f"Чат {chat_id} очищен")

