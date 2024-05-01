from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta

from Result import Result


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

    def users_search(self, vk_session, criteria_dict, token) -> dict:

        """
        Выполняет get-запрос к vk api users.search с поиском пользователей
        :param criteria_dict: словарь критерий поиска
        :return: результат запроса в виде экземпляра класса Result
        """
        url = 'https://api.vk.com/method/users.search'
        criteria_dict = {
            'sex': 1,
            'status': 1,
            'age_from': 20,
            'age_to': 45,
            'has_photo': 1,
            'count': 100,
            'access_token': token,
            'fields': 'about,sex',
            'v': '5.199'
        }

        users_list = None
        response = requests.get(url, params={**criteria_dict})
        if response.status_code == 200:
            users_list = response.json().get('response').get('items')
            users_list = self.add_photos(users_list)

        return users_list



    def add_photos(self, users_list) -> list:
        """
        Выполняет добавление информации о фото пользователей
        :param users_list: список пользователей
        :return: users_list дополненный список пользователей
        """
        for user in users_list:
            user['photos'] = self.get_user_photo(user.get('id'))

        return users_list

    def get_user_photo(self, user_id):
        result = self.vk_service.users_photos(user_id)
        photo_list = []
        photo_dict_likes = {}
        if result.success:
            try:
                photo_items = result.value.get('response').get('items')
                for item in photo_items:
                    if not item.get('likes') is None:
                        photo_dict_likes[item['sizes'][0]['url']] = item['likes']['user_likes']
                    else:
                        photo_dict_likes[item['sizes'][0]['url']] = 0

                sorted(photo_dict_likes.items(), key=lambda x: x[1], reverse=True)
            except Exception as e:
                print(f'Ошибка в получании данных из результата - {str(e)}')
        else:
            print(f'Ошибка в результате запроса - {result.error}')

        photo_list = [k for k in photo_dict_likes.keys()]

        if len(photo_list) < 3:
            photo_list
        else:
            photo_list[:3]

        return photo_list


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
                    city = item
                    break
            return city
        else:
            return None
