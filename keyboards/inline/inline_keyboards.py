from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from loader import bot


def close_operation():
    close_operation = InlineKeyboardMarkup(row_width=1)
    close_operation.add(
        InlineKeyboardButton(text='Выход из сценария', callback_data='exit_operation')
    )

    return close_operation


def search_city_inline_keyboard(answer_search_city):
    search_city_inline_keyboard = InlineKeyboardMarkup(row_width=1)

    search_city_inline_keyboard.add(
        *[InlineKeyboardButton(text=key_city, callback_data=f'{value[0]} {value[1]}') for key_city, value in answer_search_city.items()]
    )

    return search_city_inline_keyboard