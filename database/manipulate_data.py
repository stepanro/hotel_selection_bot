import json
from loader import logger
import mysql.connector
from mysql.connector import Error
import os
from config_data.config import load_dotenv


@logger.catch
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


@logger.catch
def check_table():
    connection = create_connection(host_name=host, user_name=user, user_password=password, database_name=name_database)
    cursor = connection.cursor()
    cursor.execute(f"SHOW TABLES FROM {os.getenv('NAME_DATABASE')}")
    table = [i[0] for i in cursor]
    if "users_data" not in table:
        command = f"CREATE TABLE `{name_database}`.`users_data` (" \
                  "`id` INT NOT NULL    AUTO_INCREMENT," \
                  "`users_id`            TINYTEXT NULL," \
                  "`users_name`          TINYTEXT NULL," \
                  "`users_age`           TINYTEXT NULL," \
                  "`users_country`       TINYTEXT NULL," \
                  "`users_city`          TINYTEXT NULL," \
                  "`users_phone_number`  TINYTEXT NULL," \
                  "PRIMARY KEY (`id`))" \
                  "DEFAULT CHARACTER SET = utf8;"

        cursor.execute(command)

    if "users_history" not in table:
        command = f"CREATE TABLE `{name_database}`.`users_history` (" \
                  "`id` INT NOT NULL    AUTO_INCREMENT," \
                  "`users_id`            TINYTEXT NULL," \
                  "`date_search`         DATETIME NULL," \
                  "`data_search`             JSON NULL," \
                  "PRIMARY KEY (`id`))" \
                  "DEFAULT CHARACTER SET = utf8;"
        cursor.execute(command)

    if "inline_hotel_photo_buttons" not in table:
        command = f"CREATE TABLE `{name_database}`.`inline_hotel_photo_buttons` (" \
                  "`id` INT NOT NULL       AUTO_INCREMENT," \
                  "`id_hotel`               TINYTEXT NULL," \
                  "`latitude`               TINYTEXT NULL," \
                  "`longitude`              TINYTEXT NULL," \
                  "PRIMARY KEY (`id`))" \
                  "DEFAULT CHARACTER SET = utf8;"
        cursor.execute(command)


    cursor.close()
    connection.close()

    return True


@logger.catch
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


@logger.catch
def download_user_data(*args, **kwargs):
    if check_table():

        download_user_data = "SELECT * FROM `users_data` WHERE `users_id` = {user_id}".format(user_id=kwargs['user_id'])

        connection = create_connection(host_name=host, user_name=user, user_password=password,
                                       database_name=name_database)

        cursor = connection.cursor()

        cursor.execute(operation=download_user_data)

        for result in cursor.fetchall():
            id, user_id, user_name, user_age, user_country, user_city, user_phone_number = result

            cursor.close()
            connection.close()

            return id, user_id, user_name, user_age, user_country, user_city, user_phone_number


@logger.catch
def upload_user_history(hotel_dict, user_id, time_input_city):
    if check_table():

        hotel_dict = json.dumps(hotel_dict)

        connection = create_connection(host_name=host, user_name=user, user_password=password, database_name=name_database)

        command = 'INSERT INTO `users_history` (`users_id`, `date_search`, `data_search`) VALUES (%s, %s, %s)'



        value = [user_id, time_input_city, hotel_dict]
        cursor = connection.cursor()

        cursor.execute(command, value)
        connection.commit()
        cursor.close()
        connection.close()


@logger.catch
def first_user_request(user_id):
    if check_table():
        connection = create_connection(host_name=host, user_name=user, user_password=password, database_name=name_database)

        command = f'SELECT MIN(`date_search`) FROM `users_history` WHERE `users_id` = {user_id}'

        cursor = connection.cursor()

        cursor.execute(command)

        for i_answer in cursor.fetchall():
            date_first_user_request = i_answer[0]

        cursor.close()
        connection.close()

        return date_first_user_request


@logger.catch
def get_history(user_id, start_search_date, stop_search_date):
    if check_table():
        data = list()

        connection = create_connection(host_name=host, user_name=user, user_password=password, database_name=name_database)

        command = f"SELECT `data_search` FROM `users_history` WHERE `users_id` = {user_id} AND `date_search` BETWEEN '{start_search_date}' AND '{stop_search_date}'"

        cursor = connection.cursor()

        cursor.execute(command)

        for i_answer in cursor.fetchall():
            data.append(i_answer[0])

        cursor.close()
        connection.close()

        return data


@logger.catch
def upload_inline_hotel_photo_buttons(*args, **kwargs):
    if check_table():
        id_hotel, latitude, longitude = kwargs.values()
        id_hotel, latitude, longitude = map(str, [id_hotel, latitude, longitude])

        connection = create_connection(host_name=host, user_name=user, user_password=password,
                                       database_name=name_database)

        cursor = connection.cursor()

        check_row_command = f"SELECT * FROM `inline_hotel_photo_buttons` WHERE `id_hotel` = {id_hotel}"



        cursor.execute(check_row_command)
        cursor.fetchall()
        if cursor.rowcount > 0:
            pass
        else:
            insert_row_command = f"INSERT INTO `inline_hotel_photo_buttons` (`id_hotel`, `latitude`, `longitude`) VALUE (%s, %s, %s)"
            value = [id_hotel, latitude, longitude]
            cursor.execute(insert_row_command, value)

            connection.commit()
            cursor.close()
            connection.close()


@logger.catch
def download_inline_hotel_photo_buttons(*args, **kwargs):
    id_hotel = args[0]

    connection = create_connection(host_name=host, user_name=user, user_password=password,
                                   database_name=name_database)
    cursor = connection.cursor()

    check_row_command = f"SELECT * FROM `inline_hotel_photo_buttons` WHERE `id_hotel` = {id_hotel}"

    cursor.execute(check_row_command)

    cursor.fetchall()
    if cursor.rowcount > 0:
        download_button_data_command = f"SELECT `latitude`, `longitude` FROM `inline_hotel_photo_buttons` WHERE `id_hotel` = {id_hotel}"

        cursor.execute(download_button_data_command)


        for latitude, longitude in cursor.fetchall():
            return latitude, longitude


