import logging
from aiogram import types, Dispatcher
from aiogram.filters import BaseFilter
from aiogram.types import Message, ErrorEvent
from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.dispatcher.router import Router

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BAD_WORDS = {'хуй', 'пизда', 'ебацца', 'херня', 'ебаный', 'нахуй'}

class BadWordsFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        text = message.text.lower()
        result = any(bad_word in text for bad_word in BAD_WORDS)
        logger.info(f"Проверка сообщения на плохие слова: '{message.text}' => {result}")
        return result

async def moderate_message(message: types.Message):
    try:
        await message.delete()
        logger.info(f"Удалено сообщение с плохими словами: '{message.text}'")
    except Exception as e:
        logger.error(f"Ошибка при удалении сообщения: {e}")
    raise CancelHandler()

def register_moderation_handlers(dp: Dispatcher):
    dp.message.register(moderate_message, BadWordsFilter())
    logger.info("Модерация сообщений зарегистрирована")

    # Глобальная обработка CancelHandler, чтобы он не считался ошибкой
    router = Router()

    @router.errors()
    async def cancel_handler_error(event: ErrorEvent):
        if isinstance(event.exception, CancelHandler):
            logger.info(f"Обработано исключение CancelHandler: {event.exception}")
            return True  # Ошибка обработана, дальше не передаем
        return False  # Не обрабатываем другие ошибки

    dp.include_router(router)
