from telegram_bot_calendar.detailed import DetailedTelegramCalendar
from typing import Any
from telebot.types import CallbackQuery
from loader import logger


@logger.catch
def get_calendar(is_process: bool = False, callback_data: CallbackQuery = None, **kwargs) -> Any:
    """ Функция, создающая и возвращающая объект календаря """
    if is_process:
        result, key, step = DetailedTelegramCalendar(calendar_id=kwargs['calendar_id'],
                                                     current_date=kwargs.get('current_date'),
                                                     min_date=kwargs['min_date'],
                                                     max_date=kwargs['max_date'],
                                                     locale=kwargs['locale']).process(callback_data.data)
        return result, key, step
    else:
        calendar, step = DetailedTelegramCalendar(calendar_id=kwargs['calendar_id'],
                                                  current_date=kwargs.get('current_date'),
                                                  min_date=kwargs['min_date'],
                                                  max_date=kwargs['max_date'],
                                                  locale=kwargs['locale']).build()
        return calendar, step
