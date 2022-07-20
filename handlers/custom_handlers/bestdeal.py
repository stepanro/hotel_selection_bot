from loader import bot
from states.ClassUserState import UserInfoState
from keyboards.reply.reply_keyboards import number_keyboard
from loader import logger
from telebot.types import Message


@bot.message_handler(state=UserInfoState.min_price)
@logger.catch
def min_price(message: Message) -> None:
    """ Функция обрабатывает сообщения при условии наличия статуса min_price """
    user_min_price = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_min_price.isdigit():
        with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
            data['min_price'] = user_min_price

        bot.send_message(chat_id=chat_id, text='Введите максимальную стоимость отеля в рублях')
        bot.set_state(user_id=user_id, state=UserInfoState.max_price, chat_id=chat_id)
    else:
        bot.send_message(chat_id=chat_id, text='Стоимость - это сугубо числовое значение, введите его цифрами!')
        bot.send_message(chat_id=chat_id, text='Введите минимальную стоимость отеля в рублях')


@bot.message_handler(state=UserInfoState.max_price)
@logger.catch
def max_price(message: Message) -> None:
    """ Функция обрабатывает сообщения при условии наличия статуса max_price """
    user_max_price = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_max_price.isdigit():
        with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
            data['max_price'] = user_max_price

        bot.send_message(chat_id=chat_id, text='Введите минимальное расстояние от центра в километрах')
        bot.set_state(user_id=user_id, state=UserInfoState.min_distance, chat_id=chat_id)
    else:
        bot.send_message(chat_id=chat_id, text='Стоимость - это сугубо числовое значение, введите его цифрами!')
        bot.send_message(chat_id=chat_id, text='Введите максимальную стоимость отеля в рублях')


@bot.message_handler(state=UserInfoState.min_distance)
@logger.catch
def min_distance(message: Message) -> None:
    """ Функция обрабатывает сообщения при условии наличия статуса min_distance """
    user_min_distance = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_min_distance.isdigit():
        with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
            data['min_distance'] = user_min_distance

        bot.send_message(chat_id=chat_id, text='Введите максимальное расстояние от центра в километрах')
        bot.set_state(user_id=user_id, state=UserInfoState.max_distance, chat_id=chat_id)
    else:
        bot.send_message(chat_id=chat_id, text='Расстояние - это сугубо числовое значение, введите его цифрами!')
        bot.send_message(chat_id=chat_id, text='Введите минимальное расстояние от центра в километрах')


@bot.message_handler(state=UserInfoState.max_distance)
@logger.catch
def max_distance(message: Message) -> None:
    """ Функция обрабатывает сообщения при условии наличия статуса max_distance """
    user_max_distance = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_max_distance.isdigit():
        with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
            data['max_distance'] = user_max_distance

        bot.send_message(chat_id=chat_id, text='Выберите количество отелей', reply_markup=number_keyboard())
        bot.set_state(user_id=user_id, state=UserInfoState.number_hotels, chat_id=chat_id)

    else:
        bot.send_message(chat_id=chat_id, text='Расстояние - это сугубо числовое значение, введите его цифрами!')
        bot.send_message(chat_id=chat_id, text='Введите максимальное расстояние от центра в километрах')
