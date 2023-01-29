import requests
import json
import random

#класс получения информации и фотографий людей.
class VkForParsInfo:

    def __init__(self, version='5.131', access_token=None):
        self.token = access_token
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_photo(self, idss): #получаем фотографии, передавая айдишник человека который нам нужен
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': idss, 'album_id': 'profile', 'photo_sizes': 0, 'extended': 1, 'rev': 1}
        response = requests.get(url, params={**self.params, **params})
        likes = 0
        photo_info = {}
        photos_json = []
        sorted_likes = []
        photos_info = response.json()
        for items in photos_info.values():
            for keys, values in items.items():
                if keys == 'items':
                    for each_photo_info in values:
                        for key, value in each_photo_info.items():
                            if key == 'likes':
                                likes = value.get('count')
                            if key == 'sizes':
                                sorted_pic = (sorted(value, key=lambda d: d['height']))[-5:]
                                photo_info['url'] = sorted_pic[-1].get('url')
                            if key == 'id':
                                photo_info['photo_id'] = value
                        photo_info['likes'] = likes
                        photos_json.append(photo_info)
                        sorted_likes = sorted(photos_json, key=lambda k: k['likes'])[-3:]
                        photo_info = {}

        return sorted_likes

    def users_get_free(self, sex, get_city, age_from, bot_people_id): #сюда принимаем из бота настройки для поиска
        self.sex = sex
        self.city_id = get_city
        self.age_from = age_from
        self.age_to = age_from + 4
        self.bot_people_id = bot_people_id
        self.offset = random.randint(1, 999)
        url = 'https://api.vk.com/method/users.search'
        params_1 = {
                    'sort': 0, 'offset': self.offset, 'sex': self.sex, 'count': 1, 'city': self.city_id,
                    'has_photo': 1, 'age_from': self.age_from, "age_to": self.age_to,
                    'is_closed': False
                    }
        # настройки у вк апи очень плохо работают когда я пишу is_closed 0 значит я хочу искать открытые аккаунты, но мне всё равно выдает закрытые и тогда джсон будет пустой
        # это всё я описал в боте
        response_1 = requests.get(url, params={**self.params, **params_1}).json()
        spisok = []
        spisok_url = []
        users_data = {}
        users_dates = []
        for item in response_1.values(): # все эти циклы написаны по примеру того, как мы решали это в проекте с вк-яндекс
            for keys, values in item.items():
                if keys == 'items':
                    for list in values:
                        print(list)
                        for key, value in list.items():
                            if key == 'first_name':
                                name = value
                            if key == 'id':
                                user_id = value
                            if key == 'last_name':
                                surname = value
                            if key == 'is_closed':
                                if value == True:
                                    continue
                                else:
                                    users_data['first_name'] = name
                                    users_data['last_name'] = surname
                                    users_data['link'] = f'https://vk.com/id{user_id}'
                                    photos = self.users_photo(idss=user_id)
                                    if photos != []:
                                        for photo in photos:
                                            for keys, values in photo.items():
                                                if keys == 'photo_id':
                                                    spisok.append(values)
                                                    users_data[f'{keys}'] = spisok
                                                if keys == 'url':
                                                    spisok_url.append(values)
                                                    users_data[f'{keys}'] = spisok_url
                                        users_dates.append(users_data)
                                        users_data = {}
                                        spisok=[]
                                        spisok_url = []

            with open(f'{self.bot_people_id}_data.json', 'w', encoding='utf8') as f: # тут создается джсон для каждого пользователя бота, с людьми которые будут ему высвечиваться
                json.dump(users_dates, f, sort_keys=False, ensure_ascii=False, indent=2) # после каждого вызова джсон будет обновляться и писать инфу по 1 человеку которого найдет апка
                return print("Done")
