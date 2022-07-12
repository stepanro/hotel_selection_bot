from telebot.types import BotCommand
from config_data.config import DEFAULT_COMMANDS
from loader import logger


@logger.catch
def set_default_commands(bot):
    bot.set_my_commands(
        [BotCommand(*i) for i in DEFAULT_COMMANDS]
    )

