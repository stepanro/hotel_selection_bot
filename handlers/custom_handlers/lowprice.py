import re
from datetime import datetime
import json
import time
from loader import bot
from states.ClassUserState import UserInfoState
from utils.request_api import get_hotel_list, get_photo
from keyboards.inline.inline_keyboards import close_operation, search_city_inline_keyboard
from keyboards.reply.reply_keyboards import number_keyboard, menu_keyboard, question
from utils.request_api import get_city
from telegram_bot_calendar import DetailedTelegramCalendar
from telebot.types import InputMediaPhoto
from database.manipulate_data import upload_user_history

city_dict = dict()
LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}

@bot.message_handler(commands=['lowprice'])
@bot.message_handler(func=lambda message: message.text == 'Недорогие отели')
def lowprice(message):
    bot.set_state(message.from_user.id, UserInfoState.search_city, message.chat.id)
    bot.send_message(message.from_user.id, 'В каком городе будем искать отели?', reply_markup=close_operation())


@bot.message_handler(state=UserInfoState.search_city)
def search_city(message):
    if message.text.isalpha():
        answer_search_city = get_city(message.text)
        for name_city, value in answer_search_city.items():
            city_dict[value[1]] = name_city
        bot.send_message(message.from_user.id, 'Выберете ваш город',
                         reply_markup=search_city_inline_keyboard(answer_search_city))
    else:
        bot.send_message(message.from_user.id, 'Имя города не может состоять из цифр, введите имя города еще раз.')


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('s_ci'))
def city_clarification(callback):
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    start_calendar, start_step = DetailedTelegramCalendar(calendar_id=0, locale='ru',
                                                          min_date=datetime.now().date()).build()
    bot.send_message(callback.message.chat.id, "Выберите дату заезда в отель", reply_markup=start_calendar)

    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
        key_city, destinationId_city = callback.data.split()
        data['user_id'] = callback.from_user.id
        data['name_city'] = city_dict[destinationId_city]
        data['destinationId'] = destinationId_city
        data['time_input_city'] = datetime.now()

    city_dict.clear()


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=0))
def start_date(callback):
    result, key, step = DetailedTelegramCalendar(calendar_id=0, locale='ru', min_date=datetime.now().date()).process(
        callback.data)

    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}", callback.message.chat.id, callback.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
            data['start_date'] = result
        bot.delete_message(
            callback.message.chat.id,
            callback.message.message_id
        )

        start_calendar, start_step = DetailedTelegramCalendar(calendar_id=1, locale='ru',
                                                              min_date=data['start_date']).build()
        bot.send_message(callback.message.chat.id, f"Выберите дату выезда из отеля", reply_markup=start_calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def stop_date(callback):
    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
        pass

    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=data['start_date']).process(
        callback.data)

    if not result and key:
        bot.edit_message_text(f"Выберите {LSTEP[step]}",
                              callback.message.chat.id,
                              callback.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
            data['end_date'] = result
        bot.delete_message(
            callback.message.chat.id,
            callback.message.message_id
        )

        bot.set_state(callback.from_user.id, UserInfoState.number_hotels, callback.message.chat.id)
        bot.send_message(callback.from_user.id, 'Введите количество отелей', reply_markup=number_keyboard())


@bot.message_handler(state=UserInfoState.number_hotels)
def number_hotels(message):
    bot.set_state(message.from_user.id, UserInfoState.upload_photo, message.chat.id)
    bot.send_message(message.from_user.id, 'Загружать фото?', reply_markup=question())

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['search_count_hotel'] = message.text


@bot.message_handler(state=UserInfoState.upload_photo,
                     func=lambda message: message.text == 'Да' or message.text == 'Нет')
def upload_photo(message):
    if message.text == 'Да':
        bot.set_state(message.from_user.id, UserInfoState.number_photos, message.chat.id)
        bot.send_message(message.from_user.id, 'Сколько фото загружать?', reply_markup=number_keyboard())

    elif message.text == 'Нет':
        bot.send_message(message.from_user.id, 'Вот ваши отели', reply_markup=menu_keyboard())
        bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=UserInfoState.number_photos)
def number_photo(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['search_count_photo'] = message.text

    request_answer = get_hotel_list(input_data=data)
    input_media_group_list = list()
    hotel_list = list()


    for count_hotel, hotel in enumerate(request_answer.values()):
        bot.send_chat_action(chat_id=message.from_user.id, action='upload_photo')
        answer_photo = get_photo(hotel['hotel_id'], data['search_count_photo'])
        for media_photo in answer_photo:
            input_media_group_list.append(InputMediaPhoto(media=media_photo))
        time.sleep(0.5)
        hotel_list.append(hotel["hotel_name"])

        bot.send_photo(chat_id=message.from_user.id,
                       photo=hotel['url_pic'],
                       caption='{hotel_name}\n{hotel_url}\n{all_day_in_hotel}\n{hotel_price}\n{hotel_price_all_time}'
                       .format(
                           hotel_name=f'🏨 {hotel["hotel_name"]}',
                           hotel_url=f'🌐 сайт {hotel["hotel_url"]}',
                           all_day_in_hotel=f'⌛ всего времени в отеле {(data["end_date"] - data["start_date"]).days}',
                           hotel_price=f'💲 стоимость одной ночи {hotel["hotel_price"]}',
                           hotel_price_all_time=f'💰 стоимость за все время {round(float(hotel["hotel_price"]) * (data["end_date"] - data["start_date"]).days, 2)}'
                       )
                       )


        bot.send_chat_action(chat_id=message.from_user.id, action='upload_photo')
        try:
            bot.send_media_group(chat_id=message.from_user.id, media=input_media_group_list)
        except Exception as exc:
            bot.send_message(message.from_user.id, 'не удалось загрузить фото отеля')




        bot.send_chat_action(chat_id=message.from_user.id, action='find_location')

        if count_hotel + 1 == len(request_answer.values()):
            bot.send_location(chat_id=message.from_user.id,
                              latitude=hotel['hotel_coordinate']['lat'],
                              longitude=hotel['hotel_coordinate']['lon'],
                              reply_markup=menu_keyboard()
                              )
        else:
            bot.send_location(chat_id=message.from_user.id,
                              latitude=hotel['hotel_coordinate']['lat'],
                              longitude=hotel['hotel_coordinate']['lon']
                              )
            bot.send_message(message.from_user.id, '👇' * 20)

        input_media_group_list.clear()

        data['hotels'] = hotel_list

        upload_user_history(data)

        bot.delete_state(message.from_user.id, message.chat.id)
        bot.reset_data(message.from_user.id, message.chat.id)
    bot.send_message(message.from_user.id, '👌' * 20)
