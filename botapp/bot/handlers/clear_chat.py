import asyncio

from botapp.bot.loader import bot, sent_messages
from botapp.bot.config import logger

async def clear_chat(chat_id: int, delay_seconds: int = 5):
    await asyncio.sleep(delay_seconds)
    logger.info(f"♻️ Начинаю очистку чата {chat_id}")

    message_ids = sent_messages.get(chat_id, [])
    for message_id in message_ids:
        try:
            await bot.delete_message(chat_id, message_id)
            logger.info(f"✔️ Удалено сообщение {message_id} в чате {chat_id}")
            await asyncio.sleep(0.2)  # задержка, чтобы не спамить API
        except Exception as e:
            logger.warning(f"❌ Не удалось удалить сообщение {message_id}: {e}")

    sent_messages[chat_id] = []
    logger.info(f"💬 Чат {chat_id} очищен")

