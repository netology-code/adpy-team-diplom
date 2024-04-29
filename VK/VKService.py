from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta


class VKService:
    """
    VKService предоставляет методы для работы с api vk
    """

    def users_info(self, user_id):
        """
        Выполняет get-запрос к vk api users.get с информацией о пользователе
        :param user_id:
        :return:
        """

        url = 'https://api.vk.com/method/users.get'

        params = {
            'user_ids': user_id,
            'fields': 'about,sex'
        }

        response = requests.get(url, params={**self.params, **params})

        if response.status_code == 200:
            return Result(True, response.json(), "")
        else:
            return Result(False, response.json(), response.json())

    # def get_users_info(self, vk_session, user_id) -> dict:
    #     """
    #     Выполняет запрос к vk api users.get
    #     :param vk_session: vk_api
    #     :param user_id: vk идентификатор пользователя
    #     :return: dict c информацией о пользователе
    #     """
    #
    #     params = {
    #         'user_id': user_id,
    #         'fields': 'bdate,sex,city'
    #     }
    #
    #     users_info = None
    #     try:
    #         users_info = vk_session.method('users.get', params)[0]
    #     except Exception as e:
    #         print(e)
    #
    #     return users_info

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


    def determine_age(bdate: str) -> int:
        birth_date = datetime.strptime(bdate, "%d.%m.%Y")

        return relativedelta(datetime.now(), birth_date).years