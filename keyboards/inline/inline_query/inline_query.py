from loader import bot
from utils.get_data_from_api import get_photo
from telebot.types import InlineQueryResultLocation, InlineQueryResultPhoto, InputTextMessageContent
from keyboards.reply.reply_keyboards import number_keyboard
from keyboards.inline.inline_keyboards import number_photo_keyboard
from states.ClassUserState import UserInfoState
import random
from keyboards.inline.inline_keyboards import edit_number_photo_keyboard
import time


def random_number(input_list):
    for position in input_list:
        yield random.randint(1, 100000), position


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('count_photo_question'))
def count_photo_question(callback):
    _, id_hotel = callback.data.split()
    UserInfoState.data_count_photo['id_hotel'] = id_hotel
    UserInfoState.data_count_photo['id_chat'] = callback.message.chat.id
    UserInfoState.data_count_photo['start_number'] = 10
    bot.set_state(user_id=callback.from_user.id, state=UserInfoState.upload_photo)

    res = bot.send_message(
        chat_id=callback.from_user.id,
        text='Сколько фото загружать?',
        reply_markup=number_photo_keyboard(
            id_hotel=id_hotel,
            start_number=10
        )
    )

    UserInfoState.data_count_photo['id_message'] = res.id

    edit_number_photo_keyboard()


@bot.inline_handler(func=lambda query: query.query.startswith('see_photo'))
def see_photo(query):
    try:
        _, id_hotel, count_photo = query.query.split()
        link_photo_list = get_photo(id_hotel, count_photo)

        photo_list = [InlineQueryResultPhoto(
            id=id_photo,
            photo_url=link_photo,
            thumb_url=link_photo,
        ) for id_photo, link_photo in random_number(link_photo_list)]

        bot.answer_inline_query(inline_query_id=query.id, results=photo_list, cache_time=0, is_personal=True)
    except Exception as exc:
        print(exc)


@bot.inline_handler(func=lambda query: query.query.startswith('see_geo'))
def see_geo(query):
    _, latitude, longitude = query.query.split()

    latitude, longitude = map(float, [latitude, longitude])

    geo_list = [
        InlineQueryResultLocation(
            id=random.randint(1, 10000),
            title=f'this plase {latitude}-{longitude}',
            latitude=latitude,
            longitude=longitude,
            horizontal_accuracy=0
            )
        ]

    bot.answer_inline_query(
        inline_query_id=query.id,
        results=geo_list,
        cache_time=0
    )
