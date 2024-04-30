import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from ABCRepository import ABCRepository
import os


from User import User



class SQLRepository(ABCRepository):

    def add_user(self, user: User):
        pass

    def add_favorites(self, user_vk):
        """
            Получение списка избранных vk_пользователей

            Args:
                user_id (int): VK-идентификатор пользователя

            Returns:
                list_favorites (list): список пользователей-словарей
            """
        with self.connect.cursor() as cursor:
            select_dict = []
            data = []

            select_dict.append('user_id=%s')
            data.append(str(user_id))

            select_stmt = ("SELECT first_name, last_name, age, genders.gender, profile, "
                           "photo1, photo2, photo3, cities.city"
                           " FROM favorites "
                           " INNER JOIN genders"
                           " ON favorites.user_id = genders.id"
                           " INNER JOIN cities"
                           " ON favorites.city_id = cities.id"
                           " WHERE user_id=%s")

            cursor.execute(select_stmt, tuple(data))
            list_favorites = []
            return list_favorites

    def add_exceptions(self, user_vk):
        """
                Получение vk_пользователей из черного списка

                Args:
                    user_id (int): VK-идентификатор пользователя

                Returns:
                    list_favorites (list): список пользователей-словарей
                """
        with self.connect.cursor() as cursor:
            select_dict = []
            data = []

            select_dict.append('user_id=%s')
            data.append(str(user_id))

            select_stmt = ("SELECT first_name, last_name, age, genders.gender, profile, "
                           "photo1, photo2, photo3, cities.city"
                           " FROM exceptions "
                           " INNER JOIN genders"
                           " ON exceptions.user_id = genders.id"
                           " INNER JOIN cities"
                           " ON exceptions.city_id = cities.id"
                           " WHERE user_id=%s")

            cursor.execute(select_stmt, tuple(data))

    def change_favorites(self, user_vk):
        pass

    def change_exceptions(self, user_vk):
        pass

    def delete_favorites(self, user_vk):
        pass

    def delete_exceptions(self, user_vk):
        pass

    def get_favorites(self, user_id):
        pass

    def get_exceptions(self, user_id):
        pass