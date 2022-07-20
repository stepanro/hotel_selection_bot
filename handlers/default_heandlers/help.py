from telebot.types import Message
from loader import logger
from config_data.config import DEFAULT_COMMANDS
from loader import bot


@logger.catch
@bot.message_handler(commands=['help'])
def bot_help(message: Message):
    """ Функция возвращает пользователю список доступных команд """
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, '\n'.join(text))
