from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from loader import logger

@logger.catch
def user_contact_request():
    user_contact_request = ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)

    user_contact_request.add(
        KeyboardButton(
            text='Вы готовы предоставить свой номер телефона?',
            request_contact=True,
        )
    )
    return user_contact_request


@logger.catch
def number_keyboard(one_time_keyboard=True):
    number_keyboard = ReplyKeyboardMarkup(row_width=5, one_time_keyboard=one_time_keyboard,  resize_keyboard=True)

    number_keyboard.add(
        *[KeyboardButton(text=str(number)) for number in range(1, 11)]
    )

    return number_keyboard


@logger.catch
def menu_keyboard():
    menu_keyboard = ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)

    menu_keyboard.add(
        KeyboardButton(text="🛏️ Недорогие отели"),
        KeyboardButton(text="🏨 Дорогие отели"),
        KeyboardButton(text="🏩 Лучшие отели"),
        KeyboardButton(text="📜 История запросов"),
        KeyboardButton(text="📝 Личная информация")
    )

    return menu_keyboard


@logger.catch
def question():
    question = ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
    question.add(
        KeyboardButton(text='✔ Да'),
        KeyboardButton(text='❌ Нет')
    )

    return question
