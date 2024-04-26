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

        response = requests.get(url, params={**self.params})

        if response.status_code == 200:
            return Result(True, response.json(), "")
        else:
            return Result(False, response.json(), response.json())

    def get_user_first_name(self, user_id) -> str:
        """
        Выполняет получение имени пользователя
        :param user_id: id пользователя
        :return: имя пользователя
        """
        result = self.users_info(user_id)
        users_list = []
        if result.success:
            try:
                users_list = result.value.get('response').get('items')
            except Exception as e:
                print(f'Ошибка в получании данных из результата - {str(e)}')
        else:
            print(f'Ошибка в результате запроса - {result.error}')



    def users_search(self, criteria_dict) -> Result:
        """
        Выполняет get-запрос к vk api users.search с поиском пользователей
        :param criteria_dict: словарь критерий поиска
        :return: результат запроса в виде экземпляра класса Result
        """

        url = 'https://api.vk.com/method/users.search'
        #criteria_dict
        params_loc = {
            'sex': 1,
            'status': 1,
            'age_from': 20,
            'age_to': 25,
            'count': 10,
            'fields': 'about,sex'
        }
        response = requests.get(url, params={**params_loc, **self.params})

        if response.status_code == 200:
            return Result(True, response.json(), "")
        else:
            return Result(False, response.json(), response.json())

    def get_users_list(self, criteria_dict):
        """
        Выполняет получение списка пользователей из vk
        :param criteria_dict: словарь критерий поиска
        :return: список словарей с описанием пользователей
        """
        result = self.users_search(criteria_dict)
        users_list = []
        if result.success:
            try:
                users_list = result.value.get('response').get('items')
            except Exception as e:
                print(f'Ошибка в получании данных из результата - {str(e)}')
        else:
            print(f'Ошибка в результате запроса - {result.error}')

        return users_list
