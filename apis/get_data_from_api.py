import json
import math
from loader import bot
from requests import get, codes, request
import os
import re
from config_data.config import headers
from loader import logger
from requests import Response
from apis.inline_helpers.inline_helpers import loading_inline_keyboard

no_name_user = os.getenv('NO_NAME_USER')


@logger.catch
def request_to_api(url: str, headers: dict, querystring: dict) -> Response:
    """ Функция делает API запрос и если запрос успешный возвращает ответ """
    response = get(url, headers=headers, params=querystring, timeout=30)
    if response.status_code == codes.ok:
        return response


@logger.catch
def get_city(city: str) -> dict:
    """ Функция принимает название строку и возвращает словарь со списком подобранных городов """
    url_search_city = os.getenv('URL_SEARCH_CITY')
    querystring = {"query": city,
                   "locale": "ru_RU",
                   "currency": "RUB"
                   }
    response = request_to_api(url=url_search_city, headers=headers, querystring=querystring)
    pattern = r'(?<="CITY_GROUP",).+?[\]]'
    find = re.search(pattern, response.text)
    search_dict = dict()
    if find:
        data = json.loads(f"{{{find[0]}}}")
        for i_city in data['entities']:
            sub_string = re.sub('</span>', '', re.sub(r'<span class=\'highlighted\'>', '', i_city['caption']))
            search_dict[sub_string] = ('get_city', i_city['destinationId'])
    return search_dict


@logger.catch
def get_mode(mode: str) -> str:
    """ Функция принимает команду бота и возвращает состояние для дальнейшей обработки """
    sort_order = None
    if mode == 'lowprice' or mode == 'highprice':
        if mode == 'lowprice':
            sort_order = 'PRICE'
        elif mode == 'highprice':
            sort_order = 'PRICE_HIGHEST_FIRST'
        return sort_order
    elif mode == 'bestdeal':
        sort_order = 'PRICE'
        return sort_order


@logger.catch
def get_data(response: Response) -> dict:
    """ Функция объект response и возвращает словарь """
    data = dict()
    pattern = r'(?="results":).+?(?=,"pagination")'
    find = re.search(pattern, response.text)
    if find:
        data = json.loads(f"{{{find[0]}}}")
    return data


@logger.catch
def cash_photo_link(input_photo_list: list) -> None:
    """ Функция отправляет фото из списка стороннему пользователю, для того, чтобы файлы попалив кэш телеграмма,
    иначе фото не отправляются через медиагруппу и через inline mode """
    for link_photo in input_photo_list:
        bot.send_photo(chat_id=no_name_user, photo=link_photo)


@logger.catch
def get_photo(id_hotel: str, count_photos: int) -> list:
    """ Функция принимает id отеля, количество желаемых фото и возвращает
    список фото и количество реально найденных фотографий """
    url = os.getenv('URL_PROPERTIES_GET_HOTEL_PHOTO')
    querystring = {"id": id_hotel}
    response = request("GET", url, headers=headers, params=querystring)
    pattern = r'(?="hotelImages":).+?(?=,"roomImages":)'
    find = re.search(pattern, response.text)

    photo_list = list()
    count_photo = int()

    if find:
        data = json.loads(f'{{{find[0]}}}')

        for string_with_link in data['hotelImages']:
            if count_photo == int(count_photos):
                return photo_list
            else:
                link = string_with_link['baseUrl']
                link = re.sub('{size}', 'z', link)
                requests_answer = get(link)
                if requests_answer.status_code == 200:
                    photo_list.append(requests_answer.url)
                    count_photo += 1
        else:
            return photo_list
    else:
        for _ in range(int(count_photos)):
            photo_list.append('https://img1.freepng.ru/20180621/zso/kisspng-business-click-ecommerce-'
                              'web-agency-service-plas-no-photo-5b2c4658462e10.8823241115296282482875.jpg')

        cash_photo_link(photo_list)

        return photo_list


@logger.catch
def get_hotel_list(input_data: dict, mode: str, chat_id: int) -> dict:
    """ Функция принимает данные для запроса и возвращает словарь с отелями """
    count_hotel, search_dict, querystring, search_count_hotel, destinationid, check_in, check_out, sort_order, \
        min_price, max_price = int(), dict(), dict(), int(), int(), int(), int(), int(), int(), int()
    state_load = None
    sort_order = get_mode(mode)

    if mode == 'lowprice' or mode == 'highprice':
        destinationid, _, check_in, check_out, user_id, search_count_hotel = input_data.values()
    elif mode == 'bestdeal':
        destinationid, _, check_in, check_out, user_id, min_price, max_price, \
            min_distance, max_distance, search_count_hotel = input_data.values()

    url_search_city = os.getenv('URL_PROPERTIES_LIST')

    if mode == 'lowprice' or mode == 'highprice':
        querystring = {"destinationId": destinationid, "pageNumber": "1", "pageSize": "25", "checkIn": check_in,
                       "checkOut": check_out, "adults1": "1", "sortOrder": sort_order,
                       "locale": "ru_RU", "currency": "RUB"}
    elif mode == 'bestdeal':
        querystring = {"destinationId": destinationid, "pageNumber": "1", "pageSize": "25", "checkIn": check_in,
                       "checkOut": check_out, "adults1": "1", "sortOrder": sort_order,
                       "locale": "ru_RU", "currency": "RUB", "priceMin": min_price, "priceMax": max_price}

    response = request_to_api(url=url_search_city, headers=headers, querystring=querystring)
    data = get_data(response)

    if data:
        for hotel in data['results']:

            if state_load is None:
                if count_hotel == 0:
                    count_hotel = 1
                    step = math.ceil(8 / int(search_count_hotel) * count_hotel)
                    state_load = loading_inline_keyboard(chat_id=chat_id, step=step)
                    count_hotel = 0
            elif state_load:
                step = math.ceil(8 / int(search_count_hotel) * count_hotel)
                loading_inline_keyboard(chat_id=chat_id, step=step, message_id=state_load)


            if count_hotel < int(search_count_hotel):
                if mode == 'lowprice' or mode == 'highprice':
                    if hotel.get('ratePlan') and hotel.get('landmarks') and hotel.get('optimizedThumbUrls'):
                        hotel_price = hotel['ratePlan']['price']['exactCurrent']
                    else:
                        hotel_price = 'нет данных о стоимости отеля'
                    if hotel.get('landmarks'):
                        distance_center = re.sub(',', '../utils', hotel['landmarks'][0]['distance'].split()[0])
                    else:
                        distance_center = 'нет данных о расстоянии от центра'
                    if hotel.get('optimizedThumbUrls'):
                        url_pic = hotel['optimizedThumbUrls']['srpDesktop']
                    else:
                        url_pic = 'https://img1.freepng.ru/20180621/zso/kisspng-business-click-ecommerce-web-' \
                                  'agency-service-plas-no-photo-5b2c4658462e10.8823241115296282482875.jpg'

                    search_dict[hotel['name']] = {'hotel_name': hotel['name'],
                                                  'hotel_id': hotel['id'],
                                                  'url_pic': url_pic,
                                                  'hotel_price': hotel_price,
                                                  'hotel_url': f"https://www.hotels.com/ho{hotel['id']}",
                                                  'hotel_coordinate': {'lat': hotel['coordinate']['lat'],
                                                                       'lon': hotel['coordinate']['lon']
                                                                       },
                                                  'distance_center': distance_center
                                                  }
                    count_hotel += 1

                elif mode == 'bestdeal':
                    if hotel.get('ratePlan') and hotel.get('landmarks'):
                        hotel_price = hotel['ratePlan']['price']['exactCurrent']
                        distance_center = re.sub(',', '.', hotel['landmarks'][0]['distance'].split()[0])
                    else:
                        if hotel.get('ratePlan'):
                            hotel_price = hotel['ratePlan']['price']['exactCurrent']
                            distance_center = 'нет данных о расстоянии от центра'
                        elif hotel.get('landmarks'):
                            hotel_price = 'нет данных о стоимости отеля'
                            distance_center = re.sub(',', '../utils', hotel['landmarks'][0]['distance'].split()[0])

                    if float(min_distance) < float(distance_center) < float(max_distance):
                        search_dict[hotel['name']] = {'hotel_name': hotel['name'],
                                                      'hotel_id': hotel['id'],
                                                      'url_pic': hotel['optimizedThumbUrls']['srpDesktop'],
                                                      'hotel_price': hotel_price,
                                                      'hotel_url': f"https://www.hotels.com/ho{hotel['id']}",
                                                      'hotel_coordinate': {'lat': hotel['coordinate']['lat'],
                                                                           'lon': hotel['coordinate']['lon']
                                                                           },
                                                      'distance_center': distance_center
                                                      }
                        count_hotel += 1
                temp_photo_list = get_photo(id_hotel=hotel['id'], count_photos=10)
                cash_photo_link(input_photo_list=temp_photo_list)

        bot.delete_message(chat_id=chat_id, message_id=state_load)

        return search_dict
