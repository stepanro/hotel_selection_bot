from telebot import TeleBot, apihelper
from telebot.storage import StateMemoryStorage
from config_data import config
from loguru import logger
import pytz

msk = pytz.timezone('Europe/Moscow')

logger.add('debug.log', format='{time} {level} {message}', level='DEBUG')
storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
