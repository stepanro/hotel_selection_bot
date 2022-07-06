from loader import bot
from states.ClassUserState import UserInfoState
from keyboards.reply.reply_keyboards import menu_keyboard, user_contact_request, question
from keyboards.inline.inline_keyboards import close_operation
from database.manipulate_data import upload_user_data, download_user_data


@bot.message_handler(commands=['fill_profile'])
@bot.message_handler(func=lambda message: message.text == '📝 Личная информация')
def fill_profile(message):
    if download_user_data(user_id=message.from_user.id):
        users_data = download_user_data(user_id=message.from_user.id)
        id, user_id, user_name, user_age, user_country, user_city, user_phone_number = users_data
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
            data['id'] = id

    else:
        bot.set_state(message.from_user.id, UserInfoState.name, message.chat.id)
        bot.send_message(message.from_user.id, f'{message.from_user.username} введи свое полное имя', reply_markup=close_operation())


@bot.message_handler(state=UserInfoState.intermediate_state, func=lambda message: message.text == 'Да' or message.text == 'Нет')
def user_form(message, ):
    if message.text == 'Да':
        bot.set_state(message.from_user.id, UserInfoState.name, message.chat.id)
        bot.send_message(message.from_user.id, f'{message.from_user.username} введи свое полное имя', reply_markup=close_operation())

    elif message.text == 'Нет':
        bot.send_message(message.from_user.id, 'Большое спасибо за уделенное время', reply_markup=menu_keyboard())
        bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=UserInfoState.name)
def get_name(message):
    bot.set_state(message.from_user.id, UserInfoState.age, message.chat.id)
    bot.send_message(message.from_user.id, f'{message.from_user.username} введи свой возраст', reply_markup=close_operation())

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = message.text


@bot.message_handler(state=UserInfoState.age)
def get_age(message):
    bot.set_state(message.from_user.id, UserInfoState.country, message.chat.id)
    bot.send_message(message.from_user.id, f'{message.from_user.username} введи свою страну', reply_markup=close_operation())

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['age'] = message.text


@bot.message_handler(state=UserInfoState.country)
def get_country(message):
    bot.set_state(message.from_user.id, UserInfoState.city, message.chat.id)
    bot.send_message(message.from_user.id, f'{message.from_user.username} введи свой город', reply_markup=close_operation())

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['country'] = message.text


@bot.message_handler(state=UserInfoState.city)
def get_city(message):
    bot.set_state(message.from_user.id, UserInfoState.phone_number, message.chat.id)
    bot.send_message(message.from_user.id, f'{message.from_user.username}, для отправки номера нажми на кнопку <<Вы готовы предоставить свой номер телефона?>>',
                     reply_markup=user_contact_request())
    bot.send_message(message.from_user.id, f'Если нет, можно завершить заполнение анкеты, но весь прогресс будет утерян',
                     reply_markup=close_operation())

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['city'] = message.text


@bot.message_handler(content_types=['text', 'contact'], state=UserInfoState.phone_number)
def get_phone_number(message):
    if message.contact is not None:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['phone_number'] = message.contact.phone_number
        if len(data) == 5:
            upload_user_data(
                user_id=message.from_user.id,
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
                user_id=message.from_user.id,
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
        bot.send_message(message.from_user.id, 'Вы ввели некорректный номер телефона, для отправки номера нажмите на кнопку')


@bot.callback_query_handler(lambda callback: callback.data == 'exit_operation')
def close(callback):
    bot.send_message(callback.from_user.id, 'Большое спасибо за уделенное время', reply_markup=menu_keyboard())
    bot.delete_state(callback.from_user.id, callback.message.chat.id)

