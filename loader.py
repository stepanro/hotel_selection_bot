from telebot import TeleBot, apihelper
from telebot.storage import StateMemoryStorage
from config_data import config
from loguru import logger
import pytz
from database.manipulate_data import check_table

""" Инициализируем Московский часовой пояс, для правильного отображения 
времени в базе данных(можно поменять на любой из доступных) """
msk = pytz.timezone('Europe/Moscow')

""" Настраиваем logger для логирования функций """
logger.add('debug.log', format='{time} {level} {message}', level='DEBUG')

""" Создаем экземпляр класса для работы с состояниями бота """
storage = StateMemoryStorage()

""" Создаем объект бота, для работы с ботом """
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)

""" Проверяем базу данных на наличие таблиц """
check_table()
