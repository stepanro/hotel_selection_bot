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

city_dict = dict()
LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
@bot.message_handler(func=lambda
        message: message.text == '🛏️ Недорогие отели'
                 or message.text == '🏨 Дорогие отели'
                 or message.text == '🏩 Лучшие отели'
                     )

def lowprice(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    bot.set_state(user_id=user_id, state=UserInfoState.search_city, chat_id=chat_id)

    if message.text == '/lowprice' or message.text == '🛏️ Недорогие отели':
        mode = 'lowprice'
    elif message.text == '/highprice' or message.text == '🏨 Дорогие отели':
        mode = 'highprice'
    elif message.text == '/bestdeal' or message.text == '🏩 Лучшие отели':
        mode = 'bestdeal'


    with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
        data['mode'] = mode


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


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('get_city'))
def get_name_city(callback):
    _, destinationid = callback.data.split()
    message_id = callback.message.id
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    time_input = datetime.today()
    start_date = time_input.date()

    bot.delete_message(chat_id, message_id)

    check_in = check_calendar(chat_id=chat_id, start_date=start_date)

    start_date = check_in + timedelta(days=1)

    check_out = check_calendar(chat_id=chat_id, start_date=start_date)

    with bot.retrieve_data(chat_id=chat_id, user_id=user_id) as data:
        data['user_id'] = user_id
        data['check_in'] = check_in
        data['check_out'] = check_out
        data['destinationid'] = destinationid
        data['time_input_city'] = time_input

    if data['mode'] == 'lowprice' or data['mode'] == 'highprice':
        bot.send_message(chat_id=chat_id, text='Выберите количество отелей', reply_markup=number_keyboard())
        bot.set_state(user_id=user_id, state=UserInfoState.number_hotels, chat_id=chat_id)

    elif data['mode'] == 'bestdeal':
        bot.send_message(chat_id=chat_id, text='Введите минимальную стоимость отеля в рублях')
        bot.set_state(user_id=user_id, state=UserInfoState.min_price, chat_id=chat_id)


@bot.message_handler(state=UserInfoState.number_hotels)
def number_hotels(message):
    hotel_dict = dict()

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['search_count_hotel'] = message.text

    mode = data.pop('mode')

    request_get_hotel = get_hotel_list(input_data=data, mode=mode)
    hotel_list = list()

    for count_hotel, hotel in enumerate(request_get_hotel.values()):
        time.sleep(0.5)
        try:
            bot.send_photo(chat_id=message.from_user.id,
                           photo=hotel['url_pic'],
                           caption='{hotel_name}\n{hotel_url}\n{all_day_in_hotel}\n{distance_center}\n{hotel_price}\n{hotel_price_all_time}'
                           .format(
                               hotel_name=f'🏨 {hotel["hotel_name"]}',
                               hotel_url=f'🌐 сайт {hotel["hotel_url"]}',
                               all_day_in_hotel=f'⌛ всего времени в отеле {(data["check_out"] - data["check_in"]).days}',
                               distance_center=f'📍 Дистанция от исторического центра {hotel["distance_center"]}',
                               hotel_price=f'💲 стоимость одной ночи {hotel["hotel_price"]}',
                               hotel_price_all_time=f'💰 стоимость за все время {round(float(hotel["hotel_price"]) * (data["check_out"] - data["check_in"]).days, 3)}'
                           ),
                           reply_markup=open_photo_or_geo(
                               id_hotel=hotel['hotel_id'],
                               latitude=hotel['hotel_coordinate']['lat'],
                               longitude=hotel['hotel_coordinate']['lon']
                           )
                           )
        except Exception:
            if count_hotel + 1 == len(request_get_hotel):
                bot.send_message(
                    chat_id=message.from_user.id,
                    text='К сожалению, при загрузке произошла ошибка, '
                         'пробовать еще раз запрашивать этот город безполезно.',
                    reply_markup=menu_keyboard()
                )

            else:
                bot.send_message(
                    chat_id=message.from_user.id,
                    text='К сожалению, при загрузке произошла ошибка, '
                         'пробовать еще раз запрашивать этот город безполезно.'
                )

        hotel_dict[f'🏨 {hotel["hotel_name"]}'] = {
            'photo': hotel['url_pic'],
            'hotel_url': f'🌐 сайт {hotel["hotel_url"]}',
            'all_day_in_hotel': f'⌛ всего времени в отеле {(data["check_out"] - data["check_in"]).days}',
            'distance_center': f'📍 Дистанция от исторического центра {hotel["distance_center"]}',
            'hotel_price': f'💲 стоимость одной ночи {hotel["hotel_price"]}',
            'hotel_price_all_time': f'💰 стоимость за все время {round(float(hotel["hotel_price"]) * (data["check_out"] - data["check_in"]).days, 3)}'
        }

        if count_hotel + 1 == len(request_get_hotel):
            data['hotels'] = hotel_list
            bot.delete_state(message.from_user.id, message.chat.id)

    else:
        bot.send_message(
            chat_id=message.from_user.id,
            text='Ваш запрос обработан в полном объеме.',
            reply_markup=menu_keyboard()
        )

    upload_user_history(hotel_dict, data['user_id'], data['time_input_city'])
