import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from criteria import Criteria
from Repository.abc_repository import ABCRepository
import os

from Repository.card_exceptions import CardExceptions
from Repository.card_favorites import CardFavorites
from user import User


class SQLRepository(ABCRepository):

    def add_user(self, user: User):
        """
        Добавление пользователя при регистрации
        :param user:
        :return:
        """
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
                                     user.get_about_me(),
                                     user.get_user_id(),))

            #Если пользователя нет в базе - запишем
            else:
                #Проверим надичие города в базе
                sql = """SELECT id FROM cities WHERE name=%s;"""
                cursor.execute(sql, (user.get_city()['name'],))
                result = cursor.fetchone()
                if result is None:
                    sql = """INSERT INTO cities(id, name)
                                VALUES(%s, %s);"""
                    cursor.execute(sql, (user.get_city()['id'], user.get_city()['name'],))

                sql = """INSERT INTO users(id, first_name, last_name, age, gender_id, city_id, about_me)
                                                     VALUES(%s, %s, %s, %s, %s, %s, %s);"""
                cursor.execute(sql, (user.get_user_id(),
                                     user.get_first_name(),
                                     user.get_last_name(),
                                     user.get_age(),
                                     user.get_gender(),
                                     user.get_city()['id'],
                                     user.get_about_me()))

                sql = """INSERT INTO criteria(user_id, gender_id, status, age_from, age_to, city_id, has_photo)
                                                                     VALUES(%s, %s, %s, %s, %s, %s, %s);"""

                cursor.execute(sql, (user.get_user_id(),
                                     user.get_gender(),
                                     1,
                                     user.get_age() - 5,
                                     user.get_age() + 5,
                                     user.get_city()['id'],
                                     1))

        connect.commit()
        connect.close()

    def add_favorites(self, user: User):
        """
        Добавление избранных
        :param user:
        :return:
        """
        connect = psycopg2.connect(dbname='findme',
                                   user=os.getenv(key='USER_NAME_DB'),
                                   password=os.getenv(key='USER_PASSWORD_DB'))

        with connect.cursor() as cursor:
            sql = """INSERT INTO favorites(user_id, first_name, last_name, age, gender_id, profile, 
                                    photo1, photo2, photo3, city_id)
                                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
            card = user.get_card()
            photos = card.photos
            photo1 = ''
            photo2 = ''
            photo3 = ''
            if len(photos) == 3:
                photo1 = photos[0]
                photo2 = photos[1]
                photo3 = photos[2]
            elif len(photos) == 2:
                photo1 = photos[0]
                photo2 = photos[1]
            elif len(photos) == 1:
                photo1 = photos[0]


            cursor.execute(sql, (str(user.get_user_id()),
                                 card.first_name,
                                 card.last_name,
                                 0,
                                 card.gender,
                                 'https://vk.com/id' + str(card.id),
                                 photo1,
                                 photo2,
                                 photo3,
                                 card.city_id))

        connect.commit()
        connect.close()

    def add_exceptions(self, user: User):
        """
        Добавление исключений (черный список)
        :param user:
        :return:
        """
        connect = psycopg2.connect(dbname='findme',
                                   user=os.getenv(key='USER_NAME_DB'),
                                   password=os.getenv(key='USER_PASSWORD_DB'))

        with connect.cursor() as cursor:
            sql = """INSERT INTO exceptions(user_id, first_name, last_name, age, gender_id, profile, 
                                            photo1, photo2, photo3, city_id)
                                            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
            card = user.get_card()
            photos = card.photos
            photo1 = ''
            photo2 = ''
            photo3 = ''
            if len(photos) == 3:
                photo1 = photos[0]
                photo2 = photos[1]
                photo3 = photos[2]
            elif len(photos) == 2:
                photo1 = photos[0]
                photo2 = photos[1]
            elif len(photos) == 1:
                photo1 = photos[0]

            cursor.execute(sql, (str(user.get_user_id()),
                                 card.first_name,
                                 card.last_name,
                                 0,
                                 card.gender,
                                 'https://vk.com/id' + str(card.id),
                                 photo1,
                                 photo2,
                                 photo3,
                                 card.city_id))

        connect.commit()
        connect.close()

    def delete_favorites(self, user_id, profile):
        """
        Удалить из списка избранные
        :param user_id:
        :param profile:
        :return:
        """
        connect = psycopg2.connect(dbname='findme',
                                   user=os.getenv(key='USER_NAME_DB'),
                                   password=os.getenv(key='USER_PASSWORD_DB'))
        with connect.cursor() as cursor:
            sql = """DELETE FROM favorites WHERE user_id=%s and profile=%s;"""
            cursor.execute(sql, (user_id, profile))

        connect.commit()
        connect.close()

    def delete_exceptions(self, user_id, profile):
        """
        Удаление из черного списка
        :param user_id:
        :param profile:
        :return:
        """
        connect = psycopg2.connect(dbname='findme',
                                   user=os.getenv(key='USER_NAME_DB'),
                                   password=os.getenv(key='USER_PASSWORD_DB'))
        with connect.cursor() as cursor:
            sql = """DELETE FROM exceptions WHERE user_id=%s and profile=%s;"""
            cursor.execute(sql, (user_id, profile))

        connect.commit()
        connect.close()

    def get_favorites(self, user_id):
        """
        Получить список избранных
        :param user_id:
        :return:
        """
        connect = psycopg2.connect(dbname='findme',
                                   user=os.getenv(key='USER_NAME_DB'),
                                   password=os.getenv(key='USER_PASSWORD_DB'))
        with connect.cursor() as cursor:
            sql = """SELECT favorites.user_id, favorites.first_name, favorites.last_name, favorites.age, 
                        favorites.gender_id, favorites.profile, favorites.photo1, favorites.photo2, favorites.photo3, 
                        cities.id, cities.name 
                        FROM favorites 
                        INNER JOIN cities ON favorites.city_id = cities.id
                        WHERE favorites.user_id=%s;"""
            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()
            card_list = []
            for item in result:
                card = CardFavorites()
                card.id = item[0]
                card.first_name = item[1]
                card.last_name = item[2]
                card.age = item[3]
                card.gender_id = item[4]
                card.profile = item[5]
                card.photos = [item[6], item[7], item[8]]
                card.city_id = item[9]
                card.city_name = item[10]
                card_list.append(card)

            if len(card_list) > 0:
                return card_list
            else:
                return None

    def get_exceptions(self, user_id):
        """
        Получить черный список
        :param user_id:
        :return:
        """
        connect = psycopg2.connect(dbname='findme',
                                   user=os.getenv(key='USER_NAME_DB'),
                                   password=os.getenv(key='USER_PASSWORD_DB'))
        with connect.cursor() as cursor:
            sql = """SELECT exceptions.user_id, exceptions.first_name, exceptions.last_name, exceptions.age, 
                                exceptions.gender_id, exceptions.profile, exceptions.photo1, exceptions.photo2, 
                                exceptions.photo3, cities.id, cities.name 
                                FROM exceptions 
                                INNER JOIN cities ON exceptions.city_id = cities.id
                                WHERE exceptions.user_id=%s;"""
            cursor.execute(sql, (user_id,))
            result = cursor.fetchall()
            card_list = []
            for item in result:
                card = CardExceptions()
                card.id = item[0]
                card.first_name = item[1]
                card.last_name = item[2]
                card.age = item[3]
                card.gender_id = item[4]
                card.profile = item[5]
                card.photos = [item[6], item[7], item[8]]
                card.city_id = item[9]
                card.city_name = item[10]
                card_list.append(card)

            if len(card_list) > 0:
                return card_list
            else:
                return None

    def get_user(self, user_id) -> User:
        """
        Получить зарегистрированного пользователя
        :param user_id:
        :return:
        """
        connect = psycopg2.connect(dbname='findme',
                                   user=os.getenv(key='USER_NAME_DB'),
                                   password=os.getenv(key='USER_PASSWORD_DB'))
        with connect.cursor() as cursor:
            sql = """SELECT users.first_name, users.last_name, users.age, users.gender_id , users.about_me,
                        cities.id, cities.name FROM users 
                        INNER JOIN cities ON users.city_id = cities.id
                        WHERE users.id=%s;"""
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            # Если пользователь есть, создадим экземпляр класса User
            if not result is None:
                user = User(user_id)
                user.set_first_name(result[0])
                user.set_last_name(result[1])
                user.set_age(result[2])
                user.set_gender(result[3])
                user.set_about_me(result[4])
                user.set_city({'id': result[5], 'title': result[6]})

                criteria = self.open_criteria(user_id)
                user.set_criteria(criteria)
                return user

            # Если пользователя нет
            else:
                return None


    def open_criteria(self, user_id):
        """
        Получить критерий поиска
        :param user_id:
        :return:
        """
        connect = psycopg2.connect(dbname='findme',
                                   user=os.getenv(key='USER_NAME_DB'),
                                   password=os.getenv(key='USER_PASSWORD_DB'))

        with connect.cursor() as cursor:
            sql = """SELECT criteria.id, gender_id, status, age_from, age_to, city_id, cities.name, has_photo
                        FROM criteria
                        INNER JOIN cities ON criteria.city_id = cities.id
                        WHERE user_id=%s;"""
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            if not result is None:
                criteria = Criteria()
                criteria.id = result[0]
                criteria.gender_id = 1 if result[1] == 2 else 1
                criteria.status = result[2]
                criteria.age_from = result[3]
                criteria.age_to = result[4]
                criteria.city = {'id': result[5], 'name': result[6]}
                criteria.has_photo = result[7]
                return criteria
            else:
                return Criteria()

    def save_criteria(self, user: User):
        """
        Сохранить критерий поиска
        :param user:
        :return:
        """
        connect = psycopg2.connect(dbname='findme',
                                   user=os.getenv(key='USER_NAME_DB'),
                                   password=os.getenv(key='USER_PASSWORD_DB'))

        with connect.cursor() as cursor:
            criteria = user.get_criteria()
            # Проверим надичие города в базе
            sql = """SELECT id FROM cities WHERE name=%s;"""
            cursor.execute(sql, (criteria.city['name'],))
            result = cursor.fetchone()
            if result is None:
                sql = """INSERT INTO cities(id, name)
                                                        VALUES(%s, %s);"""
                cursor.execute(sql, (criteria.city['id'], criteria.city['name'],))

            sql = """UPDATE criteria SET gender_id=%s,
                                                      status=%s, 
                                                      age_from=%s,
                                                      age_to=%s,
                                                      city_id=%s,
                                                      has_photo=%s                                            
                                                WHERE id=%s and user_id=%s;"""

            cursor.execute(sql, (criteria.gender_id,
                                 criteria.status,
                                 criteria.age_from,
                                 criteria.age_to,
                                 criteria.city['id'],
                                 criteria.has_photo,
                                 criteria.id,
                                 user.get_user_id(),))

        connect.commit()
        connect.close()
