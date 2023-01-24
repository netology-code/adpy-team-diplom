import requests
import json

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
                        photo_info['likes'] = likes
                        photos_json.append(photo_info)
                        sorted_likes = sorted(photos_json, key=lambda k: k['likes'])[-3:]
                        photo_info = {}

        return sorted_likes

    def users_get_free(self, sex, get_city): #сюда принимаем из бота настройки для поиска, сюда ещё допишу возраст от и до.
        self.sex = sex
        self.city_id = get_city
        url = 'https://api.vk.com/method/users.search'
        params_1 = {'sort': 1, 'sex': self.sex, 'count': 10, 'fields': ['bdate'], 'hometown': self.city_id,
                    'has_photo': 1, 'status': 1,
                    'can_access_closed': 1}
        response_1 = requests.get(url, params={**self.params, **params_1}).json()
        users_data = {}
        users_dates = []
        for item in response_1.values(): # все эти циклы написаны по примеру того, как мы решали это в проекте с вк-яндекс
            for keys, values in item.items():
                if keys == 'items':
                    for list in values:
                        for key, value in list.items():
                            if key == 'bdate':
                                birthday = value
                            if key == 'first_name':
                                name = value
                            if key == 'id':
                                user_id = value
                            if key == 'last_name':
                                surname = value
                            if key == 'can_access_closed':
                                if value == False:
                                    continue
                                else:
                                    users_data['first_name'] = name
                                    users_data['last_name'] = surname
                                    users_data['bdate'] = birthday
                                    users_data['link'] = f'https://vk.com/id{user_id}'
                                    photos = self.users_photo(idss=user_id)
                                    num = 0
                                    if photos != []:
                                        for photo in photos:
                                            for keys, values in photo.items():
                                                if keys == 'url':
                                                    num += 1
                                                    users_data[f'{keys} {num}'] = values
                                        users_dates.append(users_data)
                                        users_data = {}
            with open('../database.json', 'w', encoding='utf8') as f:
                json.dump(users_dates, f, sort_keys=False, ensure_ascii=False, indent=2)
            return print("Done")
