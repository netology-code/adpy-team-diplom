from VKService import VKService


class VKRepository:
    """
    VKRepository предоставляет методы для получения данных о пользователях
    """
    def get_user_first_name(self, user_id) -> str:
        """
        Выполняет получение имени пользователя
        :param user_id: id пользователя
        :return: имя пользователя
        """
        pass

    def get_users_list(self, criteria_dict) -> list:
        """
        Выполняет получение списка пользователей из vk
        :param criteria_dict: словарь критерий поиска
        :return: список словарей с описанием пользователей
        """
        pass

    def add_photos(self, users_list) -> list:
        """
        Выполняет добавление информации о фото пользователей
        :param users_list: список пользователей
        :return: users_list дополненный список пользователей
        """
        pass

    def get_user_photo(self, user_id):
        pass
