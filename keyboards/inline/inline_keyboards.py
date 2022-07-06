from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot
from states.ClassUserState import UserInfoState
import time

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


def open_photo_or_geo(id_hotel, latitude, longitude):
    open_photo = InlineKeyboardMarkup(row_width=2)
    open_photo.add(
        InlineKeyboardButton(
            text='Фото',
            callback_data=f'count_photo_question {id_hotel}'
        ),
        InlineKeyboardButton(
            text='Геопозиция',
            switch_inline_query_current_chat=f'see_geo {latitude} {longitude}'
        )
    )

    return open_photo


def edite_message(start_number):
    edite_message = InlineKeyboardMarkup(row_width=1)

    edite_message.add(InlineKeyboardButton(
        text=f'Будет удалено через {start_number}',
        callback_data=f'edite_message'
    )
    )

    return edite_message


def number_photo_keyboard(id_hotel, start_number):
    number_photo_keyboard = InlineKeyboardMarkup(row_width=3)
    number_photo_list = [InlineKeyboardButton(
        text=number,
        switch_inline_query_current_chat=f'see_photo {id_hotel} {number}') for number in range(1, 10)
    ]

    number_photo_list.append(InlineKeyboardButton(
        text=f'будет удалено через {start_number} сек',
        callback_data='callback_data'
    )
    )

    number_photo_keyboard.add(*number_photo_list)

    return number_photo_keyboard


def edit_number_photo_keyboard():

    id_hotel, chat_id, start_number, message_id = UserInfoState.data_count_photo.values()

    while start_number > 0:
        time.sleep(1)
        start_number = start_number - 1


        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=number_photo_keyboard(
                id_hotel=id_hotel,
                start_number=start_number
            )
        )
    else:
        bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )

    UserInfoState.data_count_photo = dict()

def polzunok():
    polzunok = InlineKeyboardMarkup()