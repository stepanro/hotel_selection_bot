from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from loader import logger


@logger.catch
def user_contact_request() -> ReplyKeyboardMarkup:
    """ Функция создает и возвращает reply keyboard для запроса контакта у пользователя """
    keyboard = ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)

    keyboard.add(
        KeyboardButton(
            text='Вы готовы предоставить свой номер телефона?',
            request_contact=True,
        )
    )
    return keyboard


@logger.catch
def number_keyboard(one_time_keyboard: bool = True) -> ReplyKeyboardMarkup:
    """ Функция создает и возвращает reply keyboard для выбора количества отелей """
    keyboard = ReplyKeyboardMarkup(row_width=5, one_time_keyboard=one_time_keyboard,  resize_keyboard=True)

    keyboard.add(
        *[KeyboardButton(text=str(number)) for number in range(1, 11)]
    )

    return keyboard


@logger.catch
def menu_keyboard() -> ReplyKeyboardMarkup:
    """ Функция создает и возвращает reply keyboard для основного меню """
    keyboard = ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)

    keyboard.add(
        KeyboardButton(text="🛏️ Недорогие отели"),
        KeyboardButton(text="🏨 Дорогие отели"),
        KeyboardButton(text="🏩 Лучшие отели"),
        KeyboardButton(text="📜 История запросов"),
        KeyboardButton(text="📝 Личная информация")
    )

    return keyboard


@logger.catch
def question() -> ReplyKeyboardMarkup:
    """ Функция создает и возвращает reply keyboard для вопроса да/нет """
    keyboard = ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
    keyboard.add(
        KeyboardButton(text='✔ Да'),
        KeyboardButton(text='❌ Нет')
    )

    return keyboard
