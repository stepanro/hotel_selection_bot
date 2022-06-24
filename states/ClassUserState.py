from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    """Стартовое состояние"""
    intermediate_state = State()

    """Статусы записи данных о клиенте"""
    name = State()
    age = State()
    country = State()
    city = State()
    phone_number = State()

    """Статусы запроса lowprice"""
    search_city = State()
    input_date = State()
    number_hotels = State()
    upload_photo = State()
    number_photos = State()

    """Статусы меню навигации"""

