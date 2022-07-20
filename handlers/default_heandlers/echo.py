from telebot.types import Message
from loader import bot
from keyboards.reply.reply_keyboards import menu_keyboard
import time
from loader import logger


@logger.catch
@bot.message_handler(state=None)
def bot_echo(message: Message):
    """ Функция обрабатывает сообщения без статуса, команды, и без специальных текстов """
    bot.send_message(message.from_user.id, f'Прислано сообщение {message.text}, оно не содержит '
                                           f'команду, потому и возвращаем.', reply_markup=menu_keyboard())


@logger.catch
@bot.message_handler(content_types=['photo', 'location'])
def bot_echo(message: Message):
    """ Функция удаляет все сообщения от пользователя в течение 20 секунд """
    message_id = message.id
    chat_id = message.chat.id
    time.sleep(20)
    bot.delete_message(
        chat_id=chat_id,
        message_id=message_id
    )


