import time
from loader import bot
from states.ClassUserState import UserInfoState
from utils.get_data_from_api import get_hotel_list
from keyboards.inline.inline_keyboards import close_operation, search_city_inline_keyboard, open_photo_or_geo
from keyboards.reply.reply_keyboards import menu_keyboard, number_keyboard
from utils.get_data_from_api import get_city
from datetime import datetime, timedelta
from database.manipulate_data import upload_user_history
from utils.get_date import check_calendar


@bot.message_handler(state=UserInfoState.min_price)
def min_price(message):
    min_price = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id

    if min_price.isdigit():
        with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
            data['min_price'] = min_price

        bot.send_message(chat_id=chat_id, text='Введите максимальную стоимость отеля в рублях')
        bot.set_state(user_id=user_id, state=UserInfoState.max_price, chat_id=chat_id)
    else:
        bot.send_message(chat_id=chat_id, text='Стоимость - это сугубо числовое значение, введите его цифрами!')
        bot.send_message(chat_id=chat_id, text='Введите минимальную стоимость отеля в рублях')


@bot.message_handler(state=UserInfoState.max_price)
def max_price(message):
    max_price = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id

    if max_price.isdigit():
        with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
            data['max_price'] = max_price

        bot.send_message(chat_id=chat_id, text='Введите минимальное расстояние от центра в километрах')
        bot.set_state(user_id=user_id, state=UserInfoState.min_distance, chat_id=chat_id)
    else:
        bot.send_message(chat_id=chat_id, text='Стоимость - это сугубо числовое значение, введите его цифрами!')
        bot.send_message(chat_id=chat_id, text='Введите максимальную стоимость отеля в рублях')


@bot.message_handler(state=UserInfoState.min_distance)
def min_distance(message):
    min_distance = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id

    if min_distance.isdigit():
        with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
            data['min_distance'] = min_distance

        bot.send_message(chat_id=chat_id, text='Введите максимальное расстояние от центра в километрах')
        bot.set_state(user_id=user_id, state=UserInfoState.max_distance, chat_id=chat_id)
    else:
        bot.send_message(chat_id=chat_id, text='Расстояние - это сугубо числовое значение, введите его цифрами!')
        bot.send_message(chat_id=chat_id, text='Введите минимальное расстояние от центра в километрах')


@bot.message_handler(state=UserInfoState.max_distance)
def max_distance(message):
    max_distance = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id

    if max_distance.isdigit():
        with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
            data['max_distance'] = max_distance

        bot.send_message(chat_id=chat_id, text='Выберите количество отелей', reply_markup=number_keyboard())
        bot.set_state(user_id=user_id, state=UserInfoState.number_hotels, chat_id=chat_id)

    else:
        bot.send_message(chat_id=chat_id, text='Расстояние - это сугубо числовое значение, введите его цифрами!')
        bot.send_message(chat_id=chat_id, text='Введите максимальное расстояние от центра в километрах')
