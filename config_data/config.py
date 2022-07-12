import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', 'Запустить бота'),
    ('help', 'Вывести справку'),
    ('fill_profile', 'заполнение профиля'),
    ('lowprice', 'вывод самых дешёвых отелей в городе'),
    ('highprice', ' вывод самых дорогих отелей в городе'),
    ('bestdeal', 'вывод отелей, наиболее подходящих по цене и расположению от центра'),
    ('history', 'вывод истории поиска отелей')
)

headers = {
    "X-RapidAPI-Host": os.getenv('RAPID_API_HOST'),
    "X-RapidAPI-Key": os.getenv('RAPID_API_KEY')
}
