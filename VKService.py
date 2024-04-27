import vk_api
import requests
from Result import Result


class VKService:
    """
    VKService предоставляет методы для работы с api vk
    """
    def __init__(self, access_token, version='5.131'):
        self.token = access_token
        self.version = version
        #self.input_quantity_photo = input_quantity_photo
        self.params = {'access_token': self.token, 'v': self.version}

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

    def users_search(self, criteria_dict) -> Result:

        #ss = vk_api.VkApi(token=self.token)
        #vk = ss.get_api()


        """
        Выполняет get-запрос к vk api users.search с поиском пользователей
        :param criteria_dict: словарь критерий поиска
        :return: результат запроса в виде экземпляра класса Result
        """

        url = 'https://api.vk.com/method/users.search'
        #criteria_dict
        params = {
            'sex': 111,
            'status': 1,
            'age_from': 20,
            'age_to': 25,
            'count': 10,
            'has_photo': 1,
            'fields': 'about,sex'
        }

        try:
            res = vk.users.search(**params)
        except Exception as e:
            print(e)
        response = requests.get(url, params={**params, **self.params})

        if response.status_code == 200:
            return Result(True, response.json(), "")
        else:
            return Result(False, response.json(), response.json())

    def users_photos(self, user_id) -> Result:
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': user_id,
                  'extended': 1,
                  'album_id': 'profile',
                  'photo_sizes': 1}
        response = requests.get(url, params={**self.params, **params})

        if response.status_code == 200:
            if response.json().get('error'):
                return Result(False, response.json().get('error'), str(response.json().get('error')))
            else:
                return Result(True, response.json(), "")
        else:
            return Result(False, response.json(), response.json())
