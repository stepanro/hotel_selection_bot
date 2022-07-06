from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    data_count_photo = dict()

    """Стартовое состояние"""
    intermediate_state = State()

    """Статусы записи данных о клиенте"""
    name = State()
    age = State()
    country = State()
    city = State()
    phone_number = State()

    """Статусы запроса lowprice and highprice and bestdeal"""
    search_city = State()
    input_date = State()
    number_hotels = State()
    min_price = State()
    max_price = State()
    min_distance = State()
    max_distance = State()

    """Промежуточные статусы"""
    upload_photo = State()