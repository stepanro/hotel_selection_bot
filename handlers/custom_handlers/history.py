import json
from loader import bot, logger
from utils.get_date import get_calendar
from database.manipulate_data import first_user_request, get_history
from datetime import date, timedelta
from telegram_bot_calendar.detailed import DetailedTelegramCalendar
from states.ClassUserState import DateRangeState
from telebot.types import CallbackQuery

ALL_STEPS = {'y': 'год', 'm': 'месяц', 'd': 'день'}


@bot.message_handler(commands=['history'])
@bot.message_handler(func=lambda message: message.text == '📜 История запросов')
@logger.catch
def history(message):
    """ Функция обрабатывает сообщения при условии команды /history или текста сообщения 📜 История запросов """
    chat_id = message.chat.id
    user_id = message.from_user.id

    res_date_first_user_request = first_user_request(user_id=user_id)
    if res_date_first_user_request is None:
        bot.send_message(chat_id=chat_id, text='Вы еще ничего не искали, выполните первый поиск')
    else:
        out_message = bot.send_message(chat_id=chat_id, text="Выберите дату начала поиска")

        min_date = res_date_first_user_request.date()
        today = date.today()
        calendar, step = get_calendar(calendar_id=3,
                                      current_date=today,
                                      min_date=min_date,
                                      max_date=today,
                                      locale="ru")

        bot.set_state(message.from_user.id, DateRangeState.start_search_date, message.chat.id)
        bot.send_message(message.from_user.id, f"Выберите  {ALL_STEPS[step]}", reply_markup=calendar)

        with bot.retrieve_data(chat_id=chat_id, user_id=user_id) as data:
            data['min_date'] = min_date
            data['out_message'] = out_message.message_id


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=3))
@logger.catch
def handle_arrival_date(call: CallbackQuery) -> None:
    """ Первая функция календаря, вызывает функцию календаря и возвращает inline keyboard до тех пор,
    пока функция календаря не вернет result """
    today = date.today()
    chat_id = call.message.chat.id
    user_id = call.from_user.id

    with bot.retrieve_data(chat_id=chat_id, user_id=user_id) as data:
        min_date = data['min_date']

    result, key, step = get_calendar(calendar_id=3,
                                     current_date=today,
                                     min_date=min_date,
                                     max_date=today,
                                     locale="ru",
                                     is_process=True,
                                     callback_data=call)
    if not result and key:
        bot.edit_message_text(f"Выберите {ALL_STEPS[step]}",
                              call.from_user.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['date_start_search'] = result
            out_message = data['out_message']
            bot.delete_message(chat_id=chat_id, message_id=out_message)
            bot.edit_message_text(f"Дата начала поиска {result}",
                                  call.message.chat.id,
                                  call.message.message_id)

            out_message = bot.send_message(call.from_user.id, "Выберите дату окончания поиска")
            data['out_message'] = out_message.message_id
            calendar, step = get_calendar(calendar_id=4,
                                          min_date=result,
                                          max_date=today,
                                          locale="ru",
                                          )

            bot.send_message(call.from_user.id,
                             f"Выберите {ALL_STEPS[step]}",
                             reply_markup=calendar)

            bot.set_state(call.from_user.id, DateRangeState.stop_search_date, call.message.chat.id)
            data.pop('min_date')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=4))
@logger.catch
def handle_arrival_date(call: CallbackQuery):
    """ Вторая функция календаря, вызывает функцию календаря и возвращает inline keyboard до тех пор,
    пока функция календаря не вернет result """
    today = date.today()
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    message_id = call.message.message_id

    with bot.retrieve_data(chat_id=chat_id, user_id=user_id) as data:
        min_date = data['date_start_search']

    result, key, step = get_calendar(calendar_id=4,
                                     current_date=today,
                                     min_date=min_date,
                                     max_date=today,
                                     locale="ru",
                                     is_process=True,
                                     callback_data=call)
    if not result and key:

        bot.edit_message_text(f"Выберите {ALL_STEPS[step]}",
                              chat_id=user_id,
                              message_id=message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['date_stop_search'] = result
            out_message = data.pop('out_message')
            bot.delete_message(chat_id=chat_id, message_id=out_message)

            bot.edit_message_text(f"Дата окончания поиска {result}",
                                  call.message.chat.id,
                                  call.message.message_id)

        requests_history(chat_id=chat_id, user_id=user_id)


@logger.catch
def requests_history(chat_id: int, user_id: int) -> None:
    """ Функция выводит пользователю историю его запросов с учетом даты начала и даты конца поиска """
    with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
        first_date_search = data.pop('date_start_search')
        second_date_search = data.pop('date_stop_search') + timedelta(days=1)

    res_get_history = get_history(user_id=user_id,
                                  start_search_date=first_date_search,
                                  stop_search_date=second_date_search)

    if res_get_history:
        for i_request in res_get_history:
            i_request = json.loads(i_request)
            for i_hotel in i_request.keys():
                bot.send_photo(chat_id=user_id,
                               photo=i_request[i_hotel]['photo'],
                               caption='{hotel_name}\n'
                                       '{hotel_url}\n'
                                       '{all_day_in_hotel}\n'
                                       '{distance_center}\n'
                                       '{hotel_price}\n'
                                       '{hotel_price_all_time}'
                               .format(
                                   hotel_name=i_hotel,
                                   hotel_url=i_request[i_hotel]['hotel_url'],
                                   all_day_in_hotel=i_request[i_hotel]['all_day_in_hotel'],
                                   distance_center=i_request[i_hotel]['distance_center'],
                                   hotel_price=i_request[i_hotel]['hotel_price'],
                                   hotel_price_all_time=i_request[i_hotel]['hotel_price_all_time']
                               )
                               )

        bot.delete_state(user_id, chat_id)
    else:
        bot.send_message(chat_id=chat_id, text='Данных в базе нет')
        bot.delete_state(user_id, chat_id)
