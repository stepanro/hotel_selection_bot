from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
from loguru import logger

logger.add('debug.log', format='{time} {level} {message}', level='DEBUG')
storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)

