from loader import bot
from states.ClassUserState import UserInfoState
from keyboards.reply.reply_keyboards import menu_keyboard, user_contact_request, question
from keyboards.inline.inline_keyboards import close_operation_keyboard
from database.manipulate_data import upload_user_data, download_user_data
from loader import logger
from telebot.types import Message, CallbackQuery


@bot.message_handler(commands=['fill_profile'])
@bot.message_handler(func=lambda message: message.text == '📝 Личная информация')
@logger.catch
def fill_profile(message: Message) -> None:
    """ Функция обрабатывает сообщение при условии наличия команды /fill_profile
    или сообщение будет совпадать со строкой 📝 Личная информация """
    user_id = message.from_user.id
    users_data = download_user_data(user_id=user_id)

    if users_data:
        row_id, user_id, user_name, user_age, user_country, user_city, user_phone_number = users_data
        bot.send_message(message.from_user.id,
                         'Вы уже заполняли эту форму, вот ваши данные\n'
                         'Ваше имя: {user_name}\n'
                         'Ваш возраст: {user_age}\n'
                         'Ваша страна: {user_country}\n'
                         'Ваш город: {user_city}\n'
                         'Ваш номер телефона: {user_phone_number}\n\n'
                         'Вы хотите заполнить форму еще раз?'.format(
                             user_name=user_name,
                             user_age=user_age,
                             user_country=user_country,
                             user_city=user_city,
                             user_phone_number=user_phone_number
                         ),
                         reply_markup=question())

        bot.set_state(message.from_user.id, UserInfoState.intermediate_state, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['id'] = row_id

    else:
        bot.set_state(message.from_user.id, UserInfoState.name, message.chat.id)
        bot.send_message(message.from_user.id, f'{message.from_user.username} введи свое полное имя',
                         reply_markup=close_operation_keyboard())


@bot.message_handler(state=UserInfoState.intermediate_state,
                     func=lambda message: message.text == '✔ Да' or message.text == '❌ Нет')
@logger.catch
def user_form(message: Message) -> None:
    """ Функция обрабатывает сообщение при условии наличия статуса intermediate_state и
    сообщение будет совпадать со строками ✔ Да ❌ Нет """
    if message.text == '✔ Да':
        bot.set_state(message.from_user.id, UserInfoState.name, message.chat.id)
        bot.send_message(message.from_user.id, f'{message.from_user.username} введи свое полное имя',
                         reply_markup=close_operation_keyboard())

    elif message.text == '❌ Нет':
        bot.send_message(message.from_user.id, 'Большое спасибо за уделенное время', reply_markup=menu_keyboard())
        bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=UserInfoState.name)
@logger.catch
def get_name(message: Message) -> None:
    """ Функция обрабатывает сообщение при условии наличия статуса name """
    bot.set_state(message.from_user.id, UserInfoState.age, message.chat.id)
    bot.send_message(message.from_user.id, f'{message.from_user.username} введи свой возраст',
                     reply_markup=close_operation_keyboard())

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = message.text


@bot.message_handler(state=UserInfoState.age)
@logger.catch
def get_age(message: Message) -> None:
    """ Функция обрабатывает сообщение при условии наличия статуса age """
    bot.set_state(message.from_user.id, UserInfoState.country, message.chat.id)
    bot.send_message(message.from_user.id, f'{message.from_user.username} введи свою страну',
                     reply_markup=close_operation_keyboard())

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['age'] = message.text


@bot.message_handler(state=UserInfoState.country)
@logger.catch
def get_country(message: Message) -> None:
    """ Функция обрабатывает сообщение при условии наличия статуса country """
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
    bot.send_message(message.from_user.id, f'{message.from_user.username} введи свой город',
                     reply_markup=close_operation_keyboard())

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['country'] = message.text


@bot.message_handler(state=UserInfoState.city)
@logger.catch
def get_city(message: Message) -> None:
    """ Функция обрабатывает сообщение при условии наличия статуса city """
    bot.set_state(message.from_user.id, UserInfoState.phone_number, message.chat.id)
    bot.send_message(message.from_user.id, f'{message.from_user.username}, для отправки номера нажми на кнопку '
                                           f'<<Вы готовы предоставить свой номер телефона?>>',
                     reply_markup=user_contact_request())
    bot.send_message(message.from_user.id, f'Если нет, можно завершить заполнение анкеты, '
                                           f'но весь прогресс будет утерян',
                     reply_markup=close_operation_keyboard())

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city'] = message.text


@bot.message_handler(content_types=['text', 'contact'], state=UserInfoState.phone_number)
@logger.catch
def get_phone_number(message: Message) -> None:
    """ Функция обрабатывает сообщение при условии наличия статуса phone_number и
    тип сообщения будет text bkb contact """
    user_id = message.from_user.id

    if message.contact is not None:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['phone_number'] = message.contact.phone_number
        if len(data) == 5:
            upload_user_data(
                user_id=user_id,
                user_name=data['name'],
                user_age=data['age'],
                user_country=data['country'],
                user_city=data['city'],
                user_phone_number=data['phone_number']
            )
            bot.send_message(message.from_user.id, 'Большое спасибо за уделенное время', reply_markup=menu_keyboard())
            bot.delete_state(message.from_user.id, message.chat.id)

        elif len(data) == 6:
            upload_user_data(
                user_id=user_id,
                user_name=data['name'],
                user_age=data['age'],
                user_country=data['country'],
                user_city=data['city'],
                user_phone_number=data['phone_number'],
                id=data['id']
            )

            bot.send_message(message.from_user.id, 'Большое спасибо за уделенное время', reply_markup=menu_keyboard())
            bot.delete_state(message.from_user.id, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Вы ввели некорректный номер телефона, '
                                               'для отправки номера нажмите на кнопку')


@bot.callback_query_handler(lambda callback: callback.data == 'exit_operation')
@logger.catch
def close(callback: CallbackQuery) -> None:
    """ Функция обрабатывает сообщение при условии, что data inline button будет равна exit_operation """
    bot.send_message(callback.from_user.id, 'Большое спасибо за уделенное время', reply_markup=menu_keyboard())
    bot.delete_state(callback.from_user.id, callback.message.chat.id)
