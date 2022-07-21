from loader import bot
from apis.get_data_from_api import get_photo
from telebot.types import InlineQueryResultLocation, InlineQueryResultPhoto, CallbackQuery, InlineQuery
from keyboards.inline.inline_keyboards import number_photo_keyboard, edit_number_photo_keyboard
from states.ClassUserState import UserInfoState
import random
from loader import logger


@logger.catch
def random_number(input_list: list) -> tuple[int, str]:
    """ Функция возвращает рандомное число от 1 до 100000 """
    for link in input_list:
        yield random.randint(1, 100000), link


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('count_photo_question'))
@logger.catch
def count_photo_question(callback: CallbackQuery) -> None:
    """ Функция подменяет inline клавиатуру под информацией об отеле на клавиатуру с количеством фото пользователю """
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    _, id_hotel = callback.data.split()
    bot.set_state(user_id=user_id, state=UserInfoState.upload_photo, chat_id=chat_id)
    res = bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.id,
        reply_markup=number_photo_keyboard(
            id_hotel=id_hotel,
            start_number=10
        )
    )
    start_number = 10
    id_message = res.message_id
    edit_number_photo_keyboard(start_number, id_message, chat_id, user_id, id_hotel)


@bot.inline_handler(func=lambda query: query.query.startswith('see_photo'))
@logger.catch
def see_photo(query: InlineQuery) -> None:
    """ Функция через inline mode отправляет пользователю запрашиваемые фотографии """
    _, id_hotel, count_photo = query.query.split()
    link_photo_list = get_photo(id_hotel, count_photo)
    photo_dict = {InlineQueryResultPhoto(
        id=id_photo,
        photo_url=link_photo,
        thumb_url=link_photo,
    ) for id_photo, link_photo in random_number(link_photo_list)}
    bot.answer_inline_query(inline_query_id=query.id, results=photo_dict)


@bot.inline_handler(func=lambda query: query.query.startswith('see_geo'))
@logger.catch
def see_geo(query: InlineQuery) -> None:
    """ Функция через inline mode отправляет пользователю геопозицию отеля """
    _, latitude, longitude = query.query.split()
    latitude, longitude = map(float, [latitude, longitude])
    geo_list = [
        InlineQueryResultLocation(
            id=random.randint(1, 10000),
            title=f'this place {latitude}-{longitude}',
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
