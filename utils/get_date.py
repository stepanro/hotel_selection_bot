import time
from states.ClassUserState import UserInfoState
from telegram_bot_calendar.detailed import DetailedTelegramCalendar
from loader import bot
from random import randint

LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}


def check_calendar(start_date, chat_id=None):
    temp_dict = dict()
    calendar_id = randint(1, 1000)

    def select_date_step_one(start_date):
        start_calendar, start_step = DetailedTelegramCalendar(calendar_id=calendar_id, locale='ru', min_date=start_date).build()
        bot.send_message(chat_id, "Выберите дату заезда в отель", reply_markup=start_calendar)

    @bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=calendar_id))
    def select_date_step_two(callback):
        result, key, step = DetailedTelegramCalendar(calendar_id=calendar_id, locale='ru', min_date=start_date).process(
            callback.data)

        if not result and key:
            bot.edit_message_text(f"Выберите {LSTEP[step]}", callback.message.chat.id, callback.message.message_id,
                                  reply_markup=key)
        elif result:

            bot.delete_message(
                callback.message.chat.id,
                callback.message.message_id
            )

            temp_dict['date'] = result

    select_date_step_one(start_date=start_date)

    while not temp_dict.get('date'):
        time.sleep(1)
    res = temp_dict['date']
    temp_dict.clear()

    return res
