import time
from loader import bot, msk
from states.ClassUserState import UserInfoState, DateRangeState
from apis.get_data_from_api import get_hotel_list, get_city
from keyboards.inline.inline_keyboards import close_operation_keyboard, search_city_inline_keyboard, \
    open_photo_or_geo_keyboard
from keyboards.reply.reply_keyboards import menu_keyboard, number_keyboard
from datetime import datetime, timedelta
from database.manipulate_data import upload_user_history
from utils.get_date import get_calendar
from telegram_bot_calendar import DetailedTelegramCalendar
from telebot.types import Message, CallbackQuery
from loader import logger

city_dict = dict()
ALL_STEPS = {'y': 'год', 'm': 'месяц', 'd': 'день'}


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
@bot.message_handler(func=lambda message: message.text == '🛏️ Недорогие отели'
                     or message.text == '🏨 Дорогие отели'
                     or message.text == '🏩 Лучшие отели')
@logger.catch
def lowprice(message: Message) -> None:
    """ Функция реагирует на сообщения при условии наличия команды lowprice или highprice или bestdeal или
    сообщение равно страм 🛏️ Недорогие отели 🏨 Дорогие отели 🏩 Лучшие отели """
    user_id = message.from_user.id
    chat_id = message.chat.id
    mode = str()

    bot.set_state(user_id=user_id, state=UserInfoState.search_city, chat_id=chat_id)

    if message.text == '/lowprice' or message.text == '🛏️ Недорогие отели':
        mode = 'lowprice'
    elif message.text == '/highprice' or message.text == '🏨 Дорогие отели':
        mode = 'highprice'
    elif message.text == '/bestdeal' or message.text == '🏩 Лучшие отели':
        mode = 'bestdeal'

    with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
        data['mode'] = mode

    bot.send_message(message.from_user.id, 'В каком городе будем искать отели?',
                     reply_markup=close_operation_keyboard())


@bot.message_handler(state=UserInfoState.search_city)
@logger.catch
def search_city(message: Message) -> None:
    """ Функция реагирует на сообщения при наличии статуса search_city """
    if message.text.isalpha():
        answer_search_city = get_city(message.text)

        for name_city, value in answer_search_city.items():
            city_dict[value[1]] = name_city

        bot.send_message(message.from_user.id, 'Выберете ваш город',
                         reply_markup=search_city_inline_keyboard(answer_search_city))

    else:
        bot.send_message(message.from_user.id, 'Имя города не может состоять из цифр, введите имя города еще раз.')


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('get_city'))
@logger.catch
def get_name_city(callback):
    """ Первая функция календаря реагирует на сообщения если data inline button начинается с get_city, вызывает
    функцию календаря и возвращает inline keyboard до тех пор, пока функция календаря не вернет result"""
    _, destinationid = callback.data.split()
    message_id = callback.message.id

    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    time_input = datetime.now(tz=msk)
    start_date = time_input.date()

    bot.delete_message(chat_id, message_id)

    out_message = bot.send_message(chat_id=chat_id, text="Выберите дату въезда в отель")

    calendar, step = get_calendar(calendar_id=1,
                                  current_date=start_date,
                                  min_date=start_date,
                                  max_date=start_date + timedelta(days=365),
                                  locale="ru")

    bot.set_state(user_id=user_id, state=DateRangeState.check_in, chat_id=chat_id)
    bot.send_message(chat_id=chat_id, text=f"Выберите  {ALL_STEPS[step]}", reply_markup=calendar)

    with bot.retrieve_data(chat_id=chat_id, user_id=user_id) as data:
        data['out_message'] = out_message.message_id
        data['destinationid'] = destinationid
        data['time_input_city'] = time_input


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
@logger.catch
def handle_arrival_date(callback: CallbackQuery):
    """ Вторая функция календаря, вызывает функцию календаря и возвращает inline keyboard до тех пор,
    пока функция календаря не вернет result """
    start_date = datetime.now(tz=msk).date()
    chat_id = callback.message.chat.id

    user_id = callback.from_user.id

    result, key, step = get_calendar(calendar_id=1,
                                     current_date=start_date,
                                     min_date=start_date,
                                     max_date=start_date + timedelta(days=365),
                                     locale="ru",
                                     is_process=True,
                                     callback_data=callback)

    if not result and key:
        bot.edit_message_text(f"Выберите {ALL_STEPS[step]}",
                              callback.from_user.id,
                              callback.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
            data['check_in'] = result
            out_message = data['out_message']
            bot.delete_message(chat_id=chat_id, message_id=out_message)
            bot.edit_message_text(f"Дата начала поиска {result}",
                                  callback.message.chat.id,
                                  callback.message.message_id)

            out_message = bot.send_message(callback.from_user.id, "Выберите дату выезда из отеля")
            data['out_message'] = out_message.message_id
            calendar, step = get_calendar(calendar_id=2,
                                          min_date=result,
                                          max_date=start_date + timedelta(days=365),
                                          locale="ru",
                                          )

            bot.send_message(callback.from_user.id,
                             f"Выберите {ALL_STEPS[step]}",
                             reply_markup=calendar)

            bot.set_state(callback.from_user.id, DateRangeState.check_out, callback.message.chat.id)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
@logger.catch
def handle_arrival_date(callback: CallbackQuery):
    """ Третья функция календаря, вызывает функцию календаря и возвращает inline keyboard до тех пор,
    пока функция календаря не вернет result """
    today = datetime.now(tz=msk).date()
    chat_id = callback.message.chat.id

    user_id = callback.from_user.id
    message_id = callback.message.message_id

    with bot.retrieve_data(chat_id=chat_id, user_id=user_id) as data:
        start_date = data['check_in']

    result, key, step = get_calendar(calendar_id=2,
                                     current_date=today,
                                     min_date=start_date + timedelta(days=1),
                                     max_date=today + timedelta(days=365),
                                     locale="ru",
                                     is_process=True,
                                     callback_data=callback)
    if not result and key:

        bot.edit_message_text(f"Выберите {ALL_STEPS[step]}",
                              chat_id=chat_id,
                              message_id=message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
            data['check_out'] = result
            out_message = data.pop('out_message')
            bot.delete_message(chat_id=chat_id, message_id=out_message)

            bot.edit_message_text(f"Дата окончания поиска {result}",
                                  callback.message.chat.id,
                                  callback.message.message_id)

            data['user_id'] = user_id

        set_numer_hotels(chat_id=chat_id, user_id=user_id)


@logger.catch
def set_numer_hotels(chat_id: int, user_id: int) -> None:
    """ Функция отправляет пользователю вопрос о количестве отелей """
    with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
        if data['mode'] == 'lowprice' or data['mode'] == 'highprice':
            bot.send_message(chat_id=chat_id, text='Выберите количество отелей', reply_markup=number_keyboard())
            bot.set_state(user_id=user_id, state=UserInfoState.number_hotels, chat_id=chat_id)

        elif data['mode'] == 'bestdeal':
            bot.send_message(chat_id=chat_id, text='Введите минимальную стоимость отеля в рублях')
            bot.set_state(user_id=user_id, state=UserInfoState.min_price, chat_id=chat_id)


@bot.message_handler(state=UserInfoState.number_hotels)
@logger.catch
def number_hotels(message: Message) -> None:
    """ Функция обрабатывает сообщения при условии наличия статуса number_hotels, возвращает пользователю полученный
    список отелей в форматированном виде и сохраняет поиск в базу данных """
    chat_id = message.chat.id
    user_id = message.from_user.id
    hotel_dict = dict()

    with bot.retrieve_data(chat_id=chat_id, user_id=user_id) as data:
        data['search_count_hotel'] = message.text

    mode = data.pop('mode')
    request_get_hotel = get_hotel_list(input_data=data, mode=mode, chat_id=chat_id)
    hotel_list = list()

    for count_hotel, hotel in enumerate(request_get_hotel.values()):
        time.sleep(0.6)
        if hotel['hotel_price'] == 'нет данных о стоимости отеля':
            hotel_price_all_time = hotel['hotel_price']
        else:
            price = round(float(hotel["hotel_price"]) * (data["check_out"] - data["check_in"]).days, 3)
            hotel_price_all_time = f'💰 стоимость за все время {price}'
        try:
            bot.send_photo(chat_id=message.from_user.id,
                           photo=hotel['url_pic'],
                           caption='{hotel_name}\n{hotel_url}\n{all_day_in_hotel}\n'
                                   '{distance_center}\n{hotel_price}\n{hotel_price_all_time}'
                           .format(
                               hotel_name=f'🏨 {hotel["hotel_name"]}',
                               hotel_url=f'🌐 сайт {hotel["hotel_url"]}',
                               all_day_in_hotel=f'⌛ всего времени в отеле {(data["check_out"] - data["check_in"]).days}',
                               distance_center=f'📍 Дистанция от исторического центра {hotel["distance_center"]}',
                               hotel_price=f'💲 стоимость одной ночи {hotel["hotel_price"]}',
                               hotel_price_all_time=hotel_price_all_time
                           ),
                           reply_markup=open_photo_or_geo_keyboard(
                               chat_id=chat_id,
                               user_id=user_id,
                               id_hotel=hotel['hotel_id'],
                               latitude=hotel['hotel_coordinate']['lat'],
                               longitude=hotel['hotel_coordinate']['lon']
                           )
                           )

            hotel_dict[f'🏨 {hotel["hotel_name"]}'] = {
                'photo': hotel['url_pic'],
                'hotel_url': f'🌐 сайт {hotel["hotel_url"]}',
                'hotel_price': f'💲 стоимость одной ночи {hotel["hotel_price"]}',
                'distance_center': f'📍 Дистанция от исторического центра {hotel["distance_center"]}',
                'all_day_in_hotel': f'⌛ всего времени в отеле {(data["check_out"] - data["check_in"]).days}',
                'hotel_price_all_time': hotel_price_all_time
            }
        except Exception as exc:
            logger.info(f'{datetime} {exc}')

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
    bot.delete_state(message.from_user.id, message.chat.id)
