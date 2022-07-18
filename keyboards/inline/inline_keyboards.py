from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot
from states.ClassUserState import UserInfoState
import time
from database.manipulate_data import upload_inline_hotel_photo_buttons, download_inline_hotel_photo_buttons
from loader import logger


@logger.catch
def close_operation_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text='Выход из сценария', callback_data='exit_operation')
    )
    return keyboard


@logger.catch
def search_city_inline_keyboard(answer_search_city):
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        *[InlineKeyboardButton(
            text=key_city,
            callback_data=f'{value[0]} {value[1]}') for key_city, value in answer_search_city.items()]
    )

    return keyboard


@logger.catch
def open_photo_or_geo_keyboard(chat_id, user_id, id_hotel, latitude, longitude):
    bot.set_state(user_id=user_id, state=UserInfoState.upload_photo, chat_id=chat_id)
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(
            text='Фото',
            callback_data=f'count_photo_question  {id_hotel}'
        ),
        InlineKeyboardButton(
            text='Геопозиция',
            switch_inline_query_current_chat=f'see_geo {latitude} {longitude}'
        )
    )
    upload_inline_hotel_photo_buttons(id_hotel=id_hotel, latitude=latitude, longitude=longitude)
    return keyboard


@logger.catch
def edite_message(start_number):
    edite_message = InlineKeyboardMarkup(row_width=1)

    edite_message.add(InlineKeyboardButton(
        text=f'Будет удалено через {start_number}',
        callback_data=f'edite_message'
    )
    )

    return edite_message


@logger.catch
def number_photo_keyboard(id_hotel, start_number):
    keyboard = InlineKeyboardMarkup(row_width=6)
    text_button = [InlineKeyboardButton(text='Выберите количество фото', callback_data='callback_data')]
    number_button = [
        InlineKeyboardButton(text=number, switch_inline_query_current_chat=f'see_photo {id_hotel} {number}') for number
        in range(1, 7)]
    delete_button = [InlineKeyboardButton(
        text=f'будет удалено через {start_number} сек',
        callback_data='callback_data'
    )
    ]
    keyboard.add(*text_button)
    keyboard.add(*number_button)
    keyboard.add(*delete_button)
    return keyboard


@logger.catch
def edit_number_photo_keyboard(start_number, id_message, chat_id, user_id, id_hotel):
    latitude, longitude = download_inline_hotel_photo_buttons(id_hotel)
    while start_number > 0:
        time.sleep(1)
        start_number = start_number - 1
        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=id_message,
            reply_markup=number_photo_keyboard(
                id_hotel=id_hotel,
                start_number=start_number
            )
        )
    else:
        bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=id_message,
            reply_markup=open_photo_or_geo_keyboard(
                chat_id=chat_id,
                user_id=user_id,
                id_hotel=id_hotel,
                latitude=latitude,
                longitude=longitude
            )
        )
    bot.delete_state(user_id=user_id, chat_id=chat_id)
