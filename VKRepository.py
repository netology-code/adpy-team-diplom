from VKService import VKService


class VKRepository:
    """
    VKRepository предоставляет методы для получения данных о пользователях
    """

    def __init__(self, access_token):
        self.vk_service = VKService(access_token)

    def get_user_first_name(self, user_id) -> str:
        """
        Выполняет получение имени пользователя
        :param user_id: id пользователя
        :return: имя пользователя
        """
        result = self.vk_service.users_info(user_id)
        first_name = None
        if result.success:
            try:
                first_name = result.value.get('response')[0].get('first_name')
            except Exception as e:
                print(f'Ошибка в получании данных из результата - {str(e)}')
        else:
            print(f'Ошибка в результате запроса - {result.error}')

        return first_name

    def get_users_list(self, criteria_dict) -> list:
        """
        Выполняет получение списка пользователей из vk
        :param criteria_dict: словарь критерий поиска
        :return: список словарей с описанием пользователей
        """
        result = self.vk_service.users_search(criteria_dict)
        users_list = []
        if result.success:
            try:
                users_list = result.value.get('response').get('items')
            except Exception as e:
                print(f'Ошибка в получании данных из результата - {str(e)}')
        else:
            print(f'Ошибка в результате запроса - {result.error}')

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
