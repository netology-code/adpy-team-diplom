import re

import requests
import json
from pprint import pprint

def read_token(filename):
    with open(filename, 'r') as file:
        return file.read().strip()

class VKUser:
    url = ''
    fotos_list = {}
    def __init__(self, id, name, surname, bdate, gender, city):
        self.id = id
        self.name = name
        self.surname = surname
        self.bdate = bdate
        self.gender = gender
        self.city = city

class VkDownload:
    URL = "https://api.vk.com/method/"
    def __init__(self):
        self.params =  {
        'access_token': read_token('vktoken.txt'),
        'v': '5.131'
    }

    #запрос информации пользователя бота
    def get_user_info(self, user_id):
        url = f"{self.URL}users.get"
        get_params = {
            'user_ids': user_id,
            'fields': 'bdate, city, sex'
        }

        request = requests.get(url, params={**self.params, **get_params})
        user_json = request.json()['response'][0]
        #print(user_json)


        return VKUser(user_json['id'], user_json['first_name'], user_json['last_name'], user_json['bdate'], user_json['sex'], user_json['city'])

    #поиск возможной пары
    #! пока нет параметра поиска по семейному положению
    def check_if_pair(self, request:json, origin_user:VKUser):
       bdate_pattern = r'\d{1,2}.\d{1,2}.\d{4}'
       users_list = request.json()['response']

       list_to_db = []
       for user in users_list:
           u_id = user['id'] if 'id' in user else None
           u_first_name = user['first_name'] if 'first_name' in user else None
           u_last_name = user['last_name'] if 'last_name' in user else None
           u_bdate = user['bdate'] if 'bdate' in user else None
           u_gender = user['sex'] if 'sex' in user else None
           u_city = user['city'] if 'city' in user else None

           if u_first_name and u_last_name and u_bdate and u_gender and u_city:
               #некоторые пользователи не указали год рождения, их пропускать?
               if not re.match(bdate_pattern, u_bdate):
                   pass
               #пропуск данных с DELETED
               elif u_first_name == 'DELETED':
                   pass
               else:
                   #рахница в возрасте по году рождения
                   bdate_splitted = re.split("\.", u_bdate)
                   user_bdate_splitted = re.split("\.", origin_user.bdate)
                   age_difference = int(bdate_splitted[2]) - int(user_bdate_splitted[2])

                   if u_gender != origin_user.gender and age_difference in range(-5, 6) and u_city == origin_user.city:

                       list_to_db.append(VKUser(u_id, u_first_name, u_last_name, u_bdate, u_gender, u_city))
                       # print(u_id)
                       # print(u_first_name)
                       # print(u_last_name)
                       # print(u_bdate)
                       # print(u_gender)
                       # print(u_city)

                       #self.download_fotos_vk(u_id)

       pprint(list_to_db)
       return list_to_db


    def find_possible_pairs(self, user:VKUser):
        url = f"{self.URL}users.get"
        #поиск пользователей по id, возможно есть другие варианты?
        step = 5
        start = 0
        stop = 100
        inc_step = 100
        ids_str = ''

        while step > 0:
            for elem in range(start, stop):
                ids_str += f'{elem}, '
            ids_str = ids_str[:-2]
            get_params = {
                'user_ids': ids_str,
                'fields': 'bdate, city, sex'
            }
            request = requests.get(url, params={**self.params, **get_params})
          #  pprint(request.json())
          #   check_request = request if 'response' in request else None
          #   if check_request:
          #       self.check_if_pair(request, user)
            self.check_if_pair(request, user)

            start = stop
            stop = stop + inc_step

            ids_str = ''
            step -= 1

    def download_fotos_vk(self, id):
        fotos_list = []
        url = f"{self.URL}photos.get"
        get_params = {
            'owner_id': id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1
        }
        request = requests.get(url, params = {**self.params, **get_params})
        fotos_json = request.json()
      #  pprint(fotos_json)

        likes_count = []
        foto_dict = {}
        # встречалось 'error' вместо ключа 'response'
        response_check = fotos_json['response'] if 'response' in fotos_json else None
        if response_check:
            for foto in fotos_json['response']['items']:
                # у некоторыъ фото нет key 'likes'
                if foto['likes']['count'] not in likes_count:
                    foto_dict['url'] = foto['likes']['count']

                # надо проверить как сортирует
                sorted_fd = dict(sorted(foto_dict.items(), key=lambda item: item[1]))
                sorted_fd = sorted_fd.reverse()
                for elem in list(sorted_fd)[0:3]:
                    fotos_list.append(elem)

        #pprint(fotos_list)
        # должен возвращать список с url
        return fotos_list