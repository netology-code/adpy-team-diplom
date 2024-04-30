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

    def users_search(self, vk_session, criteria_dict) -> dict:

        """
        Выполняет get-запрос к vk api users.search с поиском пользователей
        :param criteria_dict: словарь критерий поиска
        :return: результат запроса в виде экземпляра класса Result
        """

        criteria_dict = {
            'sex': 1,
            'status': 1,
            'age_from': 20,
            'age_to': 45,
            'has_photo': 1,
            'fields': 'about,sex'
        }

        users_list = None
        try:
            users_list = vk_session.method('users.search', criteria_dict)
        except Exception as e:
            print(e)

        return users_list

    # def users_photos(self, vk_session, user_id) -> Result:
    #     url = 'https://api.vk.com/method/photos.get'
    #     params = {'owner_id': user_id,
    #               'extended': 1,
    #               'album_id': 'profile',
    #               'photo_sizes': 1}
    #     response = requests.get(url, params={**self.params, **params})
    #
    #     if response.status_code == 200:
    #         if response.json().get('error'):
    #             return Result(False, response.json().get('error'), str(response.json().get('error')))
    #         else:
    #             return Result(True, response.json(), "")
    #     else:
    #         return Result(False, response.json(), response.json())

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
