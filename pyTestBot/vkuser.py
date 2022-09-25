import re
import requests
import json
from pprint import pprint

def read_token(filename):
    with open(filename, 'r') as file:
        return file.read().strip()

class VKUser:
    url = ''
    fotos_dict = {}
    relation = ''
    favourites_list = []

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
            'fields': 'bdate, city, sex, relation, blacklisted_by_me'
        }

        request = requests.get(url, params={**self.params, **get_params})
        user_json = request.json()['response'][0]
        #print(user_json)

        return VKUser(user_json['id'], user_json['first_name'], user_json['last_name'], user_json['bdate'], user_json['sex'], user_json['city'])

    #поиск возможной пары
    def check_if_pair(self, request:json, origin_user:VKUser):
       bdate_pattern = r'\d{1,2}.\d{1,2}.\d{4}'
       users_list = request.json()['response']

       list_to_db = []
       relation_allowed = [1, 6, 0]
       for user in users_list:
           u_id = user['id'] if 'id' in user else None
           u_first_name = user['first_name'] if 'first_name' in user else None
           u_last_name = user['last_name'] if 'last_name' in user else None
           u_bdate = user['bdate'] if 'bdate' in user else None
           u_gender = user['sex'] if 'sex' in user else None
           u_city = user['city'] if 'city' in user else None
           u_relation = user['relation'] if 'relation' in user else None

           if u_first_name and u_last_name and u_bdate and u_gender and u_city:
               #некоторые пользователи не указали год рождения, их пропускать?
               if not re.match(bdate_pattern, u_bdate):
                   pass
               #пропуск данных с DELETED
               elif u_first_name == 'DELETED':
                   pass
               else:
                   #разница в возрасте по году рождения
                   bdate_splitted = re.split("\.", u_bdate)
                   user_bdate_splitted = re.split("\.", origin_user.bdate)
                   age_difference = int(bdate_splitted[2]) - int(user_bdate_splitted[2])

                   if u_gender != origin_user.gender and age_difference in range(-5, 6) and u_city == origin_user.city and u_relation in relation_allowed:
                       vk_user = VKUser(u_id, u_first_name, u_last_name, u_bdate, u_gender, u_city)
                       # добавить в БД

                       fotos = self.download_fotos_vk(u_id)
                       vk_user.fotos_dict = fotos
                       list_to_db.append(vk_user)


       if len(list_to_db) > 0:
           pprint(list_to_db)

       return list_to_db


    def find_possible_pairs(self, user:VKUser):
        #использовать users.search
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
                'fields': 'bdate, city, sex, relation'
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
        url = f"{self.URL}photos.get"
        get_params = {
            'owner_id': id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1
        }
        request = requests.get(url, params = {**self.params, **get_params})
        fotos_json = request.json()

        likes_count = []
        foto_dict = {}
        sorted_fd =  {}
        foto_likes_dict = {}
        # встречалось 'error' вместо ключа 'response'
        response_check = fotos_json['response'] if 'response' in fotos_json else None
        if response_check:
            for foto in fotos_json['response']['items']:
                f_sizes = foto['sizes']
                f_url = ''
                if len(f_sizes) > 0:
                    #берет фото любого размера
                    f_url = f_sizes[0]['url']
                # у некоторыъ фото нет key 'likes'
                if foto['likes']['count'] not in likes_count:
                    foto_dict[f_url] = foto['likes']['count']

            # надо проверить как сортирует
            sorted_fd = dict(sorted(foto_dict.items(), key=lambda item: item[1]))
            sorted_fotos = list(sorted_fd)[-3:] if len(sorted_fd) >= 3 else list(sorted_fd)
            for elem in sorted_fotos:
                foto_likes_dict[elem] = sorted_fd[elem]
                #добавить в БД

        pprint(foto_likes_dict)
        # должен возвращать список с url
        return foto_likes_dict

    #в параметре fields есть аттрибут is_favourite, пока его не использую
    def add_user_to_favourites(self, user_to_add:VKUser, user:VKUser):
        print('function to add user to favourites')
        #добавить в фавориты в vk
        # еще не реализовано

        user.favourites_list.append(user_to_add.id)
        #добавить в базу данных

#черные списки
#паузу между requests