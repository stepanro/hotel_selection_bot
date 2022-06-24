from loader import bot
from keyboards.reply.reply_keyboards import menu_keyboard
from telebot.types import InputMediaPhoto, ForceReply

text = ''

media_list = [
    InputMediaPhoto(caption=text, media='https://exp.cdn-hotels.com/hotels/1000000/190000/184600/184557/74e998c6_z.jpg'),
    InputMediaPhoto(media='https://exp.cdn-hotels.com/hotels/37000000/36790000/36789900/36789845/29a6f0f3_z.jpg'),
    InputMediaPhoto(media='https://exp.cdn-hotels.com/hotels/37000000/36790000/36789900/36789845/af2490e5_z.jpg'),
    InputMediaPhoto(media='https://exp.cdn-hotels.com/hotels/37000000/36790000/36789900/36789845/9ba38dc5_z.jpg'),
    InputMediaPhoto(media='https://exp.cdn-hotels.com/hotels/1000000/190000/184600/184557/74e998c6_z.jpg'),
    InputMediaPhoto(media='https://exp.cdn-hotels.com/hotels/37000000/36790000/36789900/36789845/29a6f0f3_z.jpg'),
    InputMediaPhoto(media='https://exp.cdn-hotels.com/hotels/37000000/36790000/36789900/36789845/af2490e5_z.jpg'),
    InputMediaPhoto(media='https://exp.cdn-hotels.com/hotels/37000000/36790000/36789900/36789845/9ba38dc5_z.jpg')
]


@bot.message_handler(commands=['highprice'])
@bot.message_handler(func=lambda message: message.text == 'Дорогие отели')
def highprice(message):
    bot.send_media_group(message.from_user.id, disable_notification=True, media=media_list)
    bot.send_message(message.from_user.id, 'Большое спасибо за уделенное время', reply_markup=menu_keyboard())
    bot.delete_state(message.from_user.id, message.chat.id)
