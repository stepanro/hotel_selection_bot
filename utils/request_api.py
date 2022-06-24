import json
from datetime import datetime
from requests import get
import requests
import os
from dotenv import load_dotenv
import re
from loader import bot

load_dotenv()


def request_to_api(url, headers, querystring):
    response = get(url, headers=headers, params=querystring, timeout=10)
    if response.status_code == requests.codes.ok:
        return response



def get_city(city):
    headers = {
        "X-RapidAPI-Host": os.getenv('RAPID_API_HOST'),
        "X-RapidAPI-Key": os.getenv('RAPID_API_KEY')
    }

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
            search_dict[sub_string] = ('s_ci', i_city['destinationId'])

    return search_dict


def get_hotel_list(input_data):
    user_id, _, destinationid, _, checkIn, checkOut, search_count_hotel, search_count_photo = input_data.values()

    headers = {
        "X-RapidAPI-Host": os.getenv('RAPID_API_HOST'),
        "X-RapidAPI-Key": os.getenv('RAPID_API_KEY')
    }

    url_search_city = os.getenv('URL_PROPERTIES_LIST')
    querystring = {"destinationId": destinationid,
                   "pageNumber": "1",
                   "pageSize": search_count_hotel,
                   "checkIn": checkIn,
                   "checkOut": checkOut,
                   "adults1": "1",
                   "sortOrder": "PRICE",
                   "locale": "ru_RU",
                   "currency": "RUB"
                   }

    response = request_to_api(url=url_search_city, headers=headers, querystring=querystring)


    pattern = r'(?="results":).+?(?=,"pagination")'
    find = re.search(pattern, response.text)
    search_dict = dict()
    if find:
        data = json.loads(f"{{{find[0]}}}")

        for hotel in data['results']:
            if hotel.get('ratePlan'):
                search_dict[hotel['name']] = {'hotel_name': hotel['name'],
                                              'hotel_id': hotel['id'],
                                              'url_pic': hotel['optimizedThumbUrls']['srpDesktop'],
                                              'hotel_price': hotel['ratePlan']['price']['exactCurrent'],
                                              'hotel_url': f"https://www.hotels.com/ho{hotel['id']}",
                                              'hotel_coordinate': {'lat': hotel['coordinate']['lat'],
                                                                   'lon': hotel['coordinate']['lon']
                                                                   }
                                              }
            else:
                search_dict[hotel['name']] = {'hotel_name': hotel['name'],
                                              'hotel_id': hotel['id'],
                                              'url_pic': hotel['optimizedThumbUrls']['srpDesktop'],
                                              'hotel_price': 'данных на сайте нет',
                                              'hotel_url': f"https://www.hotels.com/ho{hotel['id']}",
                                              'hotel_coordinate': {'lat': hotel['coordinate']['lat'],
                                                                   'lon': hotel['coordinate']['lon']
                                                                   }
                                              }

        return search_dict


def get_photo(input_id_hotel, number_photos):
    url = os.getenv('URL_PROPERTIES_GET_HOTEL_PHOTO')

    querystring = {"id": input_id_hotel}

    headers = {
        "X-RapidAPI-Host": os.getenv('RAPID_API_HOST'),
        "X-RapidAPI-Key": os.getenv('RAPID_API_KEY')
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    pattern = r'(?="hotelImages":).+?(?=,"roomImages":)'
    find = re.search(pattern, response.text)

    if find:
        data = json.loads(f'{{{find[0]}}}')
    photo_list = list()
    count_photo = int()
    for string_with_link in data['hotelImages']:
        if count_photo + 1 == int(number_photos) + 1:
            return photo_list
        else:
            link = string_with_link['baseUrl']
            link = re.sub('{size}', 'z', link)
            requests_answer = requests.get(link)
            if requests_answer.status_code == 200:
                photo_list.append(requests_answer.url)
                count_photo += 1
