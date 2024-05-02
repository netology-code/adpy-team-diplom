from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta

from Criteria import Criteria
from Repository.CardFind import CardFind
from Result import Result
from User import User


class VKService:
    """
    VKService предоставляет методы для работы с api vk
    """

    def get_users_info(self, token, user_id):
        """
        Выполняет get-запрос к vk api users.get с информацией о пользователе
        :param user_id:
        :return:
        """

        url = 'https://api.vk.com/method/users.get'

        params = {
            'user_ids': user_id,
            'fields': 'bdate,sex,city',
            'access_token': token,
            'v': '5.199'
        }

        response = requests.get(url, params={**params})
        if response.status_code == 200:
            return response.json()['response'][0]
        else:
            return None

    def users_search(self, criteria: Criteria, token) -> dict:

        """
        Выполняет get-запрос к vk api users.search с поиском пользователей
        :param criteria_dict: словарь критерий поиска
        :return: результат запроса в виде экземпляра класса Result
        """
        url = 'https://api.vk.com/method/users.search'
        criteria_dict = {
            'sex': criteria.gender_id,
            'status': criteria.status,
            'age_from': criteria.age_from,
            'age_to': criteria.age_to,
            'has_photo': criteria.has_photo,
            'city': criteria.city['id'],
            'count': 100,
            'access_token': token,
            'fields': 'city, bdate, sex',
            'v': '5.199'
        }

        response = requests.get(url, params={**criteria_dict})
        if response.status_code == 200:
            users_list = []
            items = response.json().get('response').get('items')
            for item in items:
                if not item.get('city'):
                    item['city'] = {'id': criteria.city['id'], 'title': criteria.city['name']}
                temp = CardFind(item)
                if item.get('bdate'):
                    temp.age = self.determine_age(item.get('bdate'))
                users_list.append(temp)

            if len(users_list) > 0:
                self.add_photos(users_list[0], token)
                return users_list
            else:
                return None
        else:
            return None


    def add_photos(self, card, token) -> list:
        """
        Выполняет добавление информации о фото пользователей
        :param users_list: список пользователей
        :return: users_list дополненный список пользователей
        """
        card.photos = self.get_user_photo(card.id, token)
        return card


    def get_user_photo(self, user_id, token):
        result = self.users_photos(user_id, token)
        photo_dict_likes = {}
        if result.success:
            try:
                photo_items = result.value.get('response').get('items')
                for item in photo_items:
                    if not item.get('likes') is None:
                        photo_dict_likes[item['sizes'][3]['url']] = item['likes']['user_likes']
                    else:
                        photo_dict_likes[item['sizes'][3]['url']] = 0

                sorted(photo_dict_likes.items(), key=lambda x: x[1], reverse=True)
            except Exception as e:
                print(f'Ошибка в получании данных из результата - {str(e)}')
        else:
            print(f'Ошибка в результате запроса - {result.error}')

        photo_list = [k for k in photo_dict_likes.keys()]

        if len(photo_list) < 3:
            return photo_list
        else:
            return photo_list[:3]

    def users_photos(self, user_id, token) -> Result:
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': user_id,
                  'access_token': token,
                  'v': '5.199',
                  'extended': 1,
                  'album_id': 'profile',
                  'photo_sizes': 1}
        response = requests.get(url, params={**params})

        if response.status_code == 200:
            if response.json().get('error'):
                return Result(False, response.json().get('error'), str(response.json().get('error')))
            else:
                return Result(True, response.json(), "")
        else:
            return Result(False, response.json(), response.json())

    def determine_age(self, bdate: str) -> int:
        birth_date = datetime.strptime(bdate, "%d.%m.%Y")

        return relativedelta(datetime.now(), birth_date).years

    def get_city_by_name(self, token, text):
        url = 'https://api.vk.com/method/database.getCities'

        params = {
            'q': text,
            'access_token': token,
            'v': '5.199'
        }
        city = ''
        response = requests.get(url, params={**params})
        if response.status_code == 200:
            for item in response.json()['response']['items']:
                if item['title'].lower() == text:
                    city = {'id': item['id'], 'name': item['title']}
                    break
            return city
        else:
            return None
