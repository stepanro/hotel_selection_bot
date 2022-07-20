import json
from datetime import datetime, date
from loader import logger
import mysql.connector
from mysql.connector import Error, CMySQLConnection
import os
from typing import Callable, Any

hostname = os.getenv('HOSTNAME')
username = os.getenv('HOSTUSERNAME')
password = os.getenv('PASSWORD')
name_database = os.getenv('NAME_DATABASE')


@logger.catch
def create_connection(host_name: str, user_name: str, user_password: str, database_name: str) -> CMySQLConnection:
    """ Функция создает и возвращает соединение с базой данных """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=database_name
        )
        logger.info(f'{datetime.now()} соединение установлено')
    except Error as exc:
        logger.info(f'{datetime.now()} {exc}')
    return connection


@logger.catch
def check_table() -> bool:
    """ Функция проверяет наличие таблиц в базе данных """
    with create_connection(
            host_name=hostname,
            user_name=username,
            user_password=password,
            database_name=name_database
    ) as connection:
        cursor = connection.cursor()
        cursor.execute(f"SHOW TABLES FROM {os.getenv('NAME_DATABASE')}")
        table = [i[0] for i in cursor]
        if "users_data" not in table:
            command = """CREATE TABLE `{name_database}`.`users_data` (
                         `id` INT NOT NULL    AUTO_INCREMENT,
                         `users_id`            TINYTEXT NULL,
                         `users_name`          TINYTEXT NULL,
                         `users_age`           TINYTEXT NULL,
                         `users_country`       TINYTEXT NULL,
                         `users_city`          TINYTEXT NULL,
                         `users_phone_number`  TINYTEXT NULL,
                         PRIMARY KEY (`id`))
                         DEFAULT CHARACTER SET = utf8;""".format(
                name_database=name_database
            )
            cursor.execute(command)

        if "users_history" not in table:
            command = """CREATE TABLE `{name_database}`.`users_history` (
                         `id` INT NOT NULL    AUTO_INCREMENT,
                         `users_id`            TINYTEXT NULL,
                         `date_search`         DATETIME NULL,
                         `data_search`             JSON NULL,
                         PRIMARY KEY (`id`))
                         DEFAULT CHARACTER SET = utf8;""".format(
                name_database=name_database
            )
            cursor.execute(command)

        if "inline_hotel_photo_buttons" not in table:
            command = """CREATE TABLE `{name_database}`.`inline_hotel_photo_buttons` (
                         `id` INT NOT NULL       AUTO_INCREMENT,
                         `id_hotel`               TINYTEXT NULL,
                         `latitude`               TINYTEXT NULL,
                         `longitude`              TINYTEXT NULL,
                         PRIMARY KEY (`id`))
                         DEFAULT CHARACTER SET = utf8;""".format(
                name_database=name_database
            )
            cursor.execute(command)

        cursor.close()
        connection.close()
        return True


@logger.catch
def upload_user_data(**kwargs) -> None:
    """ Функция загружает в базу данных данные пользователя после заполнения профиля """
    if len(kwargs) == 6:
        user_id, user_name, user_age, user_country, user_city, user_phone_number = kwargs.values()
        upload_data = """INSERT INTO `users_data` (`users_id`, `users_name`, `users_age`, 
                         `users_country`, `users_city`, `users_phone_number`) VALUES (%s, %s, %s, %s, %s, %s)"""
        with create_connection(
                host_name=hostname,
                user_name=username,
                user_password=password,
                database_name=name_database
        ) as connection:
            value = [user_id, user_name, user_age, user_country, user_city, user_phone_number]
            cursor = connection.cursor()
            cursor.execute(upload_data, value)
            connection.commit()
            cursor.close()
            connection.close()

    elif len(kwargs) == 7:
        user_id, user_name, user_age, user_country, user_city, user_phone_number, row_id = kwargs.values()
        upload_data = """UPDATE `users_data` SET `users_id`='{user_id}', `users_name`='{user_name}', 
                         `users_age`='{user_age}', `users_country`='{user_country}', `users_city`='{user_city}', 
                         `users_phone_number`='{user_phone_number}' WHERE(`id`='{row_id}')""".format(
            user_id=user_id,
            user_name=user_name,
            user_age=user_age,
            user_country=user_country,
            user_city=user_city,
            user_phone_number=user_phone_number,
            row_id=row_id
        )
        with create_connection(
                host_name=hostname,
                user_name=username,
                user_password=password,
                database_name=name_database
        ) as connection:
            cursor = connection.cursor()
            cursor.execute(upload_data)
            connection.commit()
            cursor.close()
            connection.close()


@logger.catch
def download_user_data(user_id: int) -> tuple:
    """ Функция выгружает из базы данных данные пользователя """
    download_user_data_command = """SELECT * FROM `users_data` WHERE `users_id`={user_id}""".format(user_id=user_id)
    with create_connection(
            host_name=hostname,
            user_name=username,
            user_password=password,
            database_name=name_database
    ) as connection:
        cursor = connection.cursor()
        cursor.execute(operation=download_user_data_command)
        for result in cursor.fetchall():
            row_id, user_id, user_name, user_age, user_country, user_city, user_phone_number = result
            cursor.close()
            connection.close()
            return row_id, user_id, user_name, user_age, user_country, user_city, user_phone_number


@logger.catch
def upload_user_history(hotel_dict: dict, user_id: int, time_input_city: Callable) -> None:
    """ Функция загружает в базу данных дынные запроса пользователя """
    if check_table():
        hotel_dict = json.dumps(hotel_dict)
        with create_connection(
                host_name=hostname,
                user_name=username,
                user_password=password,
                database_name=name_database
        ) as connection:
            upload_user_history_command = """INSERT INTO `users_history` (`users_id`, `date_search`, `data_search`) 
                                             VALUES (%s, %s, %s)"""
            value = [user_id, time_input_city, hotel_dict]
            cursor = connection.cursor()
            cursor.execute(upload_user_history_command, value)
            connection.commit()
            cursor.close()
            connection.close()


@logger.catch
def first_user_request(user_id: str) -> Any:
    """ Функция возвращает дату первого запроса пользователя """
    date_first_user_request = None
    with create_connection(
            host_name=hostname,
            user_name=username,
            user_password=password,
            database_name=name_database
    ) as connection:
        command = f"SELECT MIN(`date_search`) FROM `users_history` WHERE `users_id` = {user_id}"
        cursor = connection.cursor()
        cursor.execute(command)
        for i_answer in cursor.fetchall():
            date_first_user_request = i_answer[0]
        cursor.close()
        connection.close()
        return date_first_user_request


@logger.catch
def get_history(user_id: int, start_search_date: str, stop_search_date: str) -> list:
    """ Функция возвращает данные пользователя из базы данных """
    data = list()
    with create_connection(
            host_name=hostname,
            user_name=username,
            user_password=password,
            database_name=name_database
    ) as connection:
        command = """SELECT `data_search` FROM `users_history` 
                     WHERE `users_id` = {user_id} AND `date_search` 
                     BETWEEN '{start_search_date}' AND '{stop_search_date}'""".format(
            user_id=user_id,
            start_search_date=start_search_date,
            stop_search_date=stop_search_date
        )
        cursor = connection.cursor()
        cursor.execute(command)
        for i_answer in cursor.fetchall():
            data.append(i_answer[0])
        cursor.close()
        connection.close()
        return data


@logger.catch
def upload_inline_hotel_photo_buttons(id_hotel: str, latitude: str, longitude: str) -> None:
    """ Функция загружает в базу данных данные об отелях и их местоположении для inline button """
    id_hotel, latitude, longitude = map(str, [id_hotel, latitude, longitude])
    with create_connection(
            host_name=hostname,
            user_name=username,
            user_password=password,
            database_name=name_database
    ) as connection:
        cursor = connection.cursor()
        check_row_command = """SELECT * FROM `inline_hotel_photo_buttons` 
                               WHERE `id_hotel` = {id_hotel}""".format(id_hotel=id_hotel)
        cursor.execute(check_row_command)
        cursor.fetchall()
        if cursor.rowcount > 0:
            pass
        else:
            insert_row_command = """INSERT INTO `inline_hotel_photo_buttons` 
                                    (`id_hotel`, `latitude`, `longitude`) VALUE (%s, %s, %s);"""
            value = [id_hotel, latitude, longitude]
            cursor.execute(insert_row_command, value)
            connection.commit()
            cursor.close()
            connection.close()


@logger.catch
def download_inline_hotel_photo_buttons(id_hotel: str) -> tuple[str, str]:
    """ Функция выгружает из базы данных данные об отелях для inline button """
    with create_connection(
            host_name=hostname,
            user_name=username,
            user_password=password,
            database_name=name_database
    ) as connection:
        cursor = connection.cursor()
        check_row_command = """SELECT * FROM `inline_hotel_photo_buttons` 
                               WHERE `id_hotel` = {id_hotel}""".format(id_hotel=id_hotel)
        cursor.execute(check_row_command)
        cursor.fetchall()
        if cursor.rowcount > 0:
            download_button_data_command = """SELECT `latitude`, `longitude` FROM `inline_hotel_photo_buttons` 
                                              WHERE `id_hotel` = {id_hotel}""".format(id_hotel=id_hotel)
            cursor.execute(download_button_data_command)
            for latitude, longitude in cursor.fetchall():
                return latitude, longitude
