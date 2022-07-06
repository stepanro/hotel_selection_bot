from telebot.types import Message
from loader import bot
from keyboards.reply.reply_keyboards import menu_keyboard
import time

@bot.message_handler(state=None)
def bot_echo(message: Message):
    bot.send_message(message.from_user.id, f'Прислано сообщение {message.text}, оно не содержит команду, потому и возвращаем.', reply_markup=menu_keyboard())


@bot.message_handler(content_types=['photo', 'location'])
def bot_echo(message: Message):
    message_id = message.id
    chat_id = message.chat.id
    time.sleep(20)
    bot.delete_message(
        chat_id=chat_id,
        message_id=message_id
    )


