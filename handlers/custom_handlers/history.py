from loader import bot
from utils.get_date import check_calendar
from keyboards.reply.reply_keyboards import menu_keyboard


@bot.message_handler(commands=['history'])
@bot.message_handler(func=lambda message: message.text == '📜 История')
def history(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    bot.send_message(chat_id=chat_id, text=r'Выберите дату, с которой нужно производить поиск')
    check_calendar()
    bot.delete_state(message.from_user.id, message.chat.id)
