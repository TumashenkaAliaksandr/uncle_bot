import asyncio
from botapp.templates.botapp.loader import bot
from botapp.templates.botapp.config import logger


async def clear_chat(chat_id: int, delay_seconds: int = 300):
    """
    Через delay_seconds секунд очищает чат бота, удаляя последние сообщения.

    :param chat_id: ID чата, который нужно очистить
    :param delay_seconds: задержка в секундах перед очисткой (по умолчанию 5 минут = 300 сек)
    """
    await asyncio.sleep(delay_seconds)
    logger.info(f"Начинаю очистку чата {chat_id}")

    try:
        # Получаем последние 100 сообщений (максимум, Telegram API ограничивает)
        history = await bot.get_chat_history(chat_id, limit=100)
        for message in history:
            try:
                await bot.delete_message(chat_id, message.message_id)
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение {message.message_id}: {e}")
        logger.info(f"Чат {chat_id} очищен")
    except Exception as e:
        logger.error(f"Ошибка при очистке чата {chat_id}: {e}")

# Для запуска этой функции из другого модуля:
# import clear_chat_module
# asyncio.create_task(clear_chat_module.clear_chat(chat_id))