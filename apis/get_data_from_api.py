import json
from requests import get, codes, request
import os
import re
from config_data.config import headers
from loader import logger
from requests import Response


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
def get_hotel_list(input_data: dict, mode: str) -> dict:
    """ Функция принимает данные для запроса и возвращает словарь с отелями """
    count_hotel, search_dict, querystring, search_count_hotel, destinationid, check_in, check_out, sort_order, \
        min_price, max_price = int(), dict(), dict(), int(), int(), int(), int(), int(), int(), int()

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
            if count_hotel < int(search_count_hotel):
                if mode == 'lowprice' or mode == 'highprice':
                    if hotel.get('ratePlan') and hotel.get('landmarks'):
                        hotel_price = hotel['ratePlan']['price']['exactCurrent']
                        distance_center = re.sub(',', '../utils', hotel['landmarks'][0]['distance'].split()[0])
                    else:
                        if hotel.get('ratePlan'):
                            hotel_price = hotel['ratePlan']['price']['exactCurrent']
                            distance_center = 'нет данных о расстоянии от центра'
                        elif hotel.get('landmarks'):
                            hotel_price = 'нет данных о стоимости отеля'
                            distance_center = re.sub(',', '../utils', hotel['landmarks'][0]['distance'].split()[0])

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

        return search_dict


@logger.catch
def get_photo(id_hotel: str, count_photos: int) -> tuple[list[str], int]:
    """ Функция принимает id отеля, количество желаемых фото и возвращает
    список фото и количество реально найденных фотографий """
    url = os.getenv('URL_PROPERTIES_GET_HOTEL_PHOTO')
    querystring = {"id": id_hotel}
    response = request("GET", url, headers=headers, params=querystring)
    pattern = r'(?="hotelImages":).+?(?=,"roomImages":)'
    find = re.search(pattern, response.text)

    if find:
        data = json.loads(f'{{{find[0]}}}')
    photo_list = list()
    count_photo = int()
    for string_with_link in data['hotelImages']:
        if count_photo == int(count_photos):
            return photo_list, count_photo
        else:
            link = string_with_link['baseUrl']
            link = re.sub('{size}', 'z', link)
            requests_answer = get(link)
            if requests_answer.status_code == 200:
                photo_list.append(requests_answer.url)
                count_photo += 1
    else:
        return photo_list, count_photo
