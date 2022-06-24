import json

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def create_connection(*args, **kwargs):
    host_name, user_name, user_password, database_name = kwargs.values()
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=database_name
        )

    except Error as exc:
        print(f"The error '{exc}' occurred")

    return connection


host = os.getenv('HOST')
user = os.getenv('USER')
password = os.getenv('PASSWORD')
name_database = os.getenv('NAME_DATABASE')


def check_table():
    connection = create_connection(host_name=host, user_name=user, user_password=password, database_name=name_database)
    cursor = connection.cursor()
    cursor.execute(f"SHOW TABLES FROM {os.getenv('NAME_DATABASE')}")
    table = [i[0] for i in cursor]
    if "users_data" not in table:
        command = "CREATE TABLE `hotel_selection`.`users_data` (" \
                  "`id` INT NOT NULL    AUTO_INCREMENT," \
                  "`users_id`           TINYTEXT NULL," \
                  "`users_name`         TINYTEXT NULL," \
                  "`users_age`          TINYTEXT NULL," \
                  "`users_country`      TINYTEXT NULL," \
                  "`users_city`         TINYTEXT NULL," \
                  "`users_phone_number` TINYTEXT NULL," \
                  "PRIMARY KEY (`id`))" \
                  "DEFAULT CHARACTER SET = utf8;"

        cursor.execute(command)

    if "users_history" not in table:
        command = "CREATE TABLE `hotel_selection`.`users_history` (" \
                  "`id` INT NOT NULL    AUTO_INCREMENT," \
                  "`users_id`           TINYTEXT NULL," \
                  "`name_city`          TYNYTEXT NULL," \
                  "`destinationId`      TINYTEXT NULL," \
                  "`start_date`         DATE NULL," \
                  "`end_date`           DATE NULL," \
                  "`search_count_hotel` TINYTEXT NULL," \
                  "`search_count_photo` TINYTEXT NULL," \
                  "PRIMARY KEY (`id`))" \
                  "DEFAULT CHARACTER SET = utf8;"

        cursor.execute(command)
    cursor.close()
    connection.close()

    return True


def upload_user_data(*args, **kwargs):
    if check_table():
        if len(kwargs) == 6:
            user_id, user_name, user_age, user_country, user_city, user_phone_number = kwargs.values()

            upload_data = 'INSERT INTO `users_data` (`users_id`, `users_name`, `users_age`, `users_country`, `users_city`, `users_phone_number`) VALUES (%s, %s, %s, %s, %s, %s)'

            connection = create_connection(host_name=host, user_name=user, user_password=password, database_name=name_database)

            value = [user_id, user_name, user_age, user_country, user_city, user_phone_number]
            cursor = connection.cursor()
            cursor.execute(upload_data, value)
            connection.commit()

            cursor.close()
            connection.close()

        elif len(kwargs) == 7:
            user_id, user_name, user_age, user_country, user_city, user_phone_number, id = kwargs.values()

            upload_data = f"UPDATE `users_data` SET `users_id`='{user_id}', `users_name`='{user_name}', `users_age`='{user_age}', `users_country`='{user_country}', `users_city`='{user_city}', `users_phone_number`='{user_phone_number}' WHERE(`id`='{id}')"

            connection = create_connection(host_name=host, user_name=user, user_password=password, database_name=name_database)

            cursor = connection.cursor()
            cursor.execute(upload_data)
            connection.commit()

            cursor.close()
            connection.close()


def download_user_data(*args, **kwargs):
    if check_table():

        download_user_data = "SELECT * FROM `users_data` WHERE `users_id` = {user_id}".format(user_id=kwargs['user_id'])

        connection = create_connection(host_name=host, user_name=user, user_password=password, database_name=name_database)

        cursor = connection.cursor()

        cursor.execute(download_user_data)
        if cursor:
            for id, user_id, user_name, user_age, user_country, user_city, user_phone_number in cursor.fetchall():
                return id, user_id, user_name, user_age, user_country, user_city, user_phone_number
            cursor.close()
            connection.close()
        else:
            cursor.close()
            connection.close()
            return None


def upload_user_history(input_data):
    if check_table():
        user_id, name_city, destinationId, time_input_city, start_date, end_date, search_count_hotel, search_count_photo, hotels = input_data.values()
        connection = create_connection(host_name=host, user_name=user, user_password=password, database_name=name_database)
        hotels = json.dumps({'hotels': hotels})
        command = 'INSERT INTO `users_history` (`users_id`, `name_city`, `destinationId`, `time_input_city`, `hotels`, `start_date`, `end_date`, `search_count_hotel`, `search_count_photo`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'

        value = [user_id, name_city, destinationId, time_input_city, hotels, start_date, end_date, search_count_hotel, search_count_photo]
        cursor = connection.cursor()

        cursor.execute(command, value)
        connection.commit()
        cursor.close()
        connection.close()
