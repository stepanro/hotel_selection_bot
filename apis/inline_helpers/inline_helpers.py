from loader import logger, bot
from typing import Any
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime


@logger.catch
def loading_inline_keyboard(chat_id: int, step: int, message_id: int = None) -> Any:
    load = '🟩'
    no_load = '🟥'

    keyboard = InlineKeyboardMarkup(row_width=8)
    keyboard.add(*[InlineKeyboardButton(text=load, callback_data='data') if count + 1 <= step else
                   InlineKeyboardButton(text=no_load, callback_data='data') for count in range(8)])

    if message_id is None:
        res_message = bot.send_message(chat_id=chat_id, text='Ожидаем, все скоро будет', reply_markup=keyboard)
        message_id = res_message.message_id
        return message_id

    else:
        try:
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=keyboard)
        except Exception as exc:
            logger.info(f'{datetime} {exc}')
