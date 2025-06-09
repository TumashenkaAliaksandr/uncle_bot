from botapp.bot.loader import bot, sent_messages

async def send_and_store(chat_id: int, text: str, **kwargs):
    message = await bot.send_message(chat_id, text, **kwargs)
    sent_messages.setdefault(chat_id, []).append(message.message_id)
    return message
