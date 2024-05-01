import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from Repository.ABCRepository import ABCRepository
import os
from User import User


class SQLRepository(ABCRepository):

    def add_user(self, user: User):
        connect = psycopg2.connect(dbname='findme',
                                        user=os.getenv(key='USER_NAME_DB'),
                                        password=os.getenv(key='USER_PASSWORD_DB'))
        with connect.cursor() as cursor:
            #Проверим есть ли пользователь в базе
            sql = """SELECT id FROM users WHERE id=%s;"""
            cursor.execute(sql, (user.get_user_id(),))
            result = cursor.fetchone()
            #Если пользователь уже есть, то обновим данные
            if not result is None:
                sql = """UPDATE users SET first_name=%s,
                                          last_name=%s, 
                                          age=%s,
                                          gender_id=%s,
                                          city_id=%s,
                                          about_me=%s                                            
                        WHERE id=%s;"""
                cursor.execute(sql, (user.get_first_name(),
                                     user.get_last_name(),
                                     user.get_age(),
                                     user.get_gender(),
                                     user.get_city()['id'],
                                     user.get_about_name(),
                                     user.get_user_id(),))

                # "UPDATE table_name SET update_column_name=(%s)"
                # " WHERE ref_column_id_value = (%s)",
                # ("column_name", "value_you_want_to_update",));
            #Если пользователя нет в базе - запишем
            else:
                #Проверим надичие города в базе
                sql = """SELECT id FROM cities WHERE name=%s;"""
                cursor.execute(sql, (user.get_city()['title'],))
                result = cursor.fetchone()
                if result is None:
                    sql = """INSERT INTO cities(id, name)
                                VALUES(%s, %s);"""
                    cursor.execute(sql, (user.get_city()['id'], user.get_city()['title'],))

                sql = """INSERT INTO users(id, first_name, last_name, age, gender_id, city_id, about_me)
                                                     VALUES(%s, %s, %s, %s, %s, %s, %s);"""
                cursor.execute(sql, (user.get_user_id(),
                                     user.get_first_name(),
                                     user.get_last_name(),
                                     user.get_age(),
                                     user.get_gender(),
                                     user.get_city()['id'],
                                     user.get_about_name()))

        connect.commit()
        connect.close()

    def add_favorites(self, user_vk):
        """
            Получение списка избранных vk_пользователей

            Args:
                user_id (int): VK-идентификатор пользователя

            Returns:
                list_favorites (list): список пользователей-словарей
            """
        # with self.connect.cursor() as cursor:
        #     select_dict = []
        #     data = []
        #
        #     select_dict.append('user_id=%s')
        #     data.append(str(user_id))
        #
        #     select_stmt = ("SELECT first_name, last_name, age, genders.gender, profile, "
        #                    "photo1, photo2, photo3, cities.city"
        #                    " FROM favorites "
        #                    " INNER JOIN genders"
        #                    " ON favorites.user_id = genders.id"
        #                    " INNER JOIN cities"
        #                    " ON favorites.city_id = cities.id"
        #                    " WHERE user_id=%s")
        #
        #     cursor.execute(select_stmt, tuple(data))
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
        # with self.connect.cursor() as cursor:
        #     select_dict = []
        #     data = []
        #
        #     select_dict.append('user_id=%s')
        #     data.append(str(user_id))
        #
        #     select_stmt = ("SELECT first_name, last_name, age, genders.gender, profile, "
        #                    "photo1, photo2, photo3, cities.city"
        #                    " FROM exceptions "
        #                    " INNER JOIN genders"
        #                    " ON exceptions.user_id = genders.id"
        #                    " INNER JOIN cities"
        #                    " ON exceptions.city_id = cities.id"
        #                    " WHERE user_id=%s")
        #
        #     cursor.execute(select_stmt, tuple(data))

        list_favorites = []
        return list_favorites

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