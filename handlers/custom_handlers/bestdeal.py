from loader import bot
from keyboards.reply.reply_keyboards import menu_keyboard


@bot.message_handler(commands=['bestdeal'])
@bot.message_handler(func=lambda message: message.text == 'лучшие отели')
def bestdeal(message):
    bot.send_message(message.from_user.id, 'Большое спасибо за уделенное время', reply_markup=menu_keyboard())

    bot.delete_state(message.from_user.id, message.chat.id)
