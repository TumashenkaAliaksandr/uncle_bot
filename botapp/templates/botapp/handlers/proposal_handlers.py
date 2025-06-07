import asyncio
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from botapp.templates.botapp.handlers.clear_chat import clear_chat
from botapp.templates.botapp.keyboards import keyboard
from botapp.templates.botapp.loader import sent_messages, bot

router = Router()

# Замените на реальный Telegram ID администратора музыкантов
MUSICIAN_ADMIN_ID = 83027638

# Функция отправки сообщения с сохранением ID для последующей очистки
async def send_and_store(chat_id: int, text: str, **kwargs) -> types.Message:
    message = await bot.send_message(chat_id, text, **kwargs)
    sent_messages.setdefault(chat_id, []).append(message.message_id)
    return message

# Состояния для FSM — ожидание ввода предложения
class ProposalStates(StatesGroup):
    waiting_for_proposal = State()

# Обработчик нажатия кнопки "Написать предложение музыкантам"
@router.message(lambda message: message.text == "✒️ Написать")
async def ask_proposal(message: types.Message, state: FSMContext):
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)
    await send_and_store(message.chat.id, "Пожалуйста, напишите ваше Имя и данные для связи\nЕсли предложение заинтересует музыкантов\nОни с вами обязательно свяжуться!")
    await state.set_state(ProposalStates.waiting_for_proposal)


# Обработчик получения текста предложения от пользователя
@router.message(ProposalStates.waiting_for_proposal)
async def receive_proposal(message: types.Message, state: FSMContext):
    user = message.from_user
    user_mention = f"@{user.username}" if user.username else user.full_name
    proposal_text = (
        f"Новое предложение от {user_mention} (id: {user.id}):\n\n{message.text}"
    )
    full_text = f"📩 Сообщение прислано из бота:\n\n{proposal_text}"

    # Отправляем сообщение администратору в личные сообщения и сохраняем ID
    sent = await bot.send_message(MUSICIAN_ADMIN_ID, full_text)
    sent_messages.setdefault(MUSICIAN_ADMIN_ID, []).append(sent.message_id)

    # Подтверждаем пользователю отправку и возвращаем главное меню
    await send_and_store(message.chat.id, "Спасибо! Ваше предложение отправлено музыкантам.", reply_markup=keyboard)

    # Сохраняем ID сообщения пользователя для удаления
    sent_messages.setdefault(message.chat.id, []).append(message.message_id)

    # Запускаем асинхронную очистку сообщений через 5 минут (300 секунд)
    asyncio.create_task(clear_chat(message.chat.id, delay_seconds=300))
    asyncio.create_task(clear_chat(MUSICIAN_ADMIN_ID, delay_seconds=300))

    # Завершаем состояние FSM
    await state.clear()
