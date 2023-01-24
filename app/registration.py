import requests

# класс нужен для регистрации и сохранения инфы о человеке который зарегистрировался
class VKRegistration:

    def __init__(self, version='5.131', access_token=None, user_id=None):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id, 'fields': 'sex'}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

