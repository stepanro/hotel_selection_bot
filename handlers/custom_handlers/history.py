import json

from loader import bot
from utils.get_date import check_calendar
from database.manipulate_data import first_user_request, get_history
from datetime import datetime, timedelta
from keyboards.reply.reply_keyboards import menu_keyboard


@bot.message_handler(commands=['history'])
@bot.message_handler(func=lambda message: message.text == '📜 История запросов')
def history(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    res_date_first_user_request = first_user_request(user_id=user_id)
    if res_date_first_user_request is None:
        bot.send_message(chat_id=chat_id, text='Вы еще ничего не искали, выполните первый поиск')
    else:
        start_date = res_date_first_user_request.date()
        stop_date = datetime.now().date()

        bot.send_message(chat_id=chat_id, text='Вы выполняли первый поиск {date_first_user_request}\nВыберите дату, с которой нужно производить поиск'.format(date_first_user_request=res_date_first_user_request))
        first_date_search = check_calendar(start_date=start_date, stop_date=stop_date, chat_id=chat_id)

        second_date_search = check_calendar(start_date=first_date_search, stop_date=stop_date, chat_id=chat_id)
        second_date_search = second_date_search + timedelta(days=1)

        res_get_history = get_history(user_id=user_id, start_search_date=first_date_search, stop_search_date=second_date_search)

        if res_get_history:
            for i_request in res_get_history:
                i_request = json.loads(i_request)
                for i_hotel in i_request.keys():
                    bot.send_photo(chat_id=message.from_user.id,
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

            bot.delete_state(message.from_user.id, message.chat.id)
        else:
            bot.send_message(chat_id=chat_id, text='Данных в базе нет')
