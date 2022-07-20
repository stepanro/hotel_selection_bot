from telebot.types import Message
from loader import bot, logger
from keyboards.reply.reply_keyboards import menu_keyboard


@logger.catch
@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    """ Функция обрабатывает команду /start и возвращает пользователю клавиатуру с меню """
    bot.send_message(message.from_user.id, f'Привет, {message.from_user.full_name}!', reply_markup=menu_keyboard())





