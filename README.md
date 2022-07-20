#  Hotel selection bot

---
### russian version

## О боте:
Бот предназначен для поиска и сортировки отелей, запрашиваемых с 
сайта [www.rapidapi.com](https://rapidapi.com/apidojo/api/hotels4/). В боте реализованы такие функции как:
* /lowprice - запрос города, времени въезда и отъезда, количества отелей. 
  Сортировка по умолчанию с недорогих отелей к дорогим.
* /highprice - запрос города, времени въезда и отъезда, количества отелей. 
  Сортировка по умолчанию от дорогих отелей к недорогим.
* /bestdeal - запрос города, времени въезда и отъезда, минимальной допустимой стоимости отеля, 
  максимально допустимой стоимости отеля, минимального расстояния от исторического центра, 
  максимального расстояния от исторического центра, количества отелей. 
  Сортировка по умолчанию от недорогих отелей к дорогим.
* /fill_profile - запрос имени, запрос возраста, запрос страны, запрос города, запрос контакта(номера телефона)
* /history - запрос даты начала поиска истории запростов, запрос даты окончания поиска истории запросов
---
## Установка:
1. Клонирование репозитория:
    - Устанавливаем GIT на сервер командой `git init`
    - С помощью команды `git clone (url)` клонируем репозиторий на ваш сервер
2. Устанавливаем все зависимости командой `pip install -r requirement.txt`
3. Устанавливаем базу данных Mysql:
    - Устанавливаем Mysql server `apt install mysql-server`
    - Создаем пользователя
    - Создаем бузу данных `hotel_secection`
4. Настраиваем бота, создав и заполнив файл `.env`, образцом для заполнения является файл `.env.template`
5. Запускаем бота командой `python3 main.py`
---
### english version
## About the bot:
The bot is designed to search and sort hotels requested from
website [www.rapidapi.com](https://rapidapi.com/apidojo/api/hotels4/). The bot has the following features:
* /lowprice - request for city, time of arrival and departure, number of hotels.
  Sort by default from cheap to expensive hotels.
* /highprice - request for city, time of arrival and departure, number of hotels.
  Sorting by default from expensive to cheap hotels.
* /bestdeal - request city, time of arrival and departure, minimum allowable cost of the hotel,
  the maximum allowable cost of the hotel, the minimum distance from the historical center,
  the maximum distance from the historical center, the number of hotels.
  Default sorting from cheap to expensive hotels.
* /fill_profile - name request, age request, country request, city request, contact request (phone number)
* /history - request for the start date of the search for the history of requests, request for the end date of the search for the history of requests
---
## Installation:
1. Cloning the repository.
    - Install GIT on the server with the `git init` command
    - Using the `git clone (url)` command, clone the repository to your server
2. Install all dependencies with the command `pip install -r requirement.txt`
3. Install the MySQL database:
     - Install Mysql server `apt install mysql-server`
     - Create a user
     - Create the `hotel_secection` data base
4. Set up the bot by creating and filling in the `.env` file, the sample for filling is the `.env.template` file
5. Run the bot with the command `python3 main.py`
