import os
from dotenv import load_dotenv

import sqlalchemy
from psycopg2 import errors
from sqlalchemy import create_engine, exc, and_
from sqlalchemy.orm import sessionmaker

from ORMTableStructure import get_class_cols
from ORMTableStructure import Users, Favorites, Exceptions
from Repository.ABCRepository import ABCRepository


class ORMRepository(ABCRepository):

    def get_engine(self) -> sqlalchemy.Engine:

        """
        Формирует движок Sqlalchemy

        Выводной параметр:
        - движок sqlalchemy
        """

        load_dotenv()

        dbname = 'findme'
        user = os.getenv(key='USER_NAME_DB')
        password = os.getenv(key='USER_PASSWORD_DB')
        host = 'localhost'
        port = '5432'

        # Создание DNS-ссылки и запуск движка
        dns_link = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        return create_engine(dns_link)


    def start_add_table_session(self, dict_user:dict, class_object:object) -> None:

        """
        Инициирует сессию по добавлению новых значений в конкретную таблицу из БД

        Вводные параметры:
        - dict_user: словарь содержащий значения, которыми необходимо заполнить таблицу
        - class_object: объект класса, содержащего структуру таблицы
        """

        # Запуск движка и инициация сессии
        engine = self.get_engine()
        session_class = sessionmaker(bind=engine)
        session = session_class()

        # Попытка добавления данных в таблицу
        try:
            model = class_object(**dict_user)
            session.add(model)
            session.commit()
            session.close()

        except (exc.IntegrityError,
                errors.UniqueViolation,
                exc.DataError,
                errors.InvalidTextRepresentation,
                errors.UndefinedTable,
                exc.ProgrammingError,
                exc.PendingRollbackError) as e:
            print(f'Ошибка при добавлении следующего словаря {dict_user}')
            print('Описание ошибки:', e, sep='\n')
            pass


    def check_cols(self, col_list:list, dict_user:dict) -> bool:

        """
        Проверяет наличие всех нужных ключей словаря dict_user, отражающих столбцы
        созданных таблиц. Проверка осуществляется относительно списка col_list.

        Вводные параметры:
        - col_list: список фактических столбцов конкретной таблицы, содержащейся в БД
        - dict_user: словарь содержащий значения, которыми необходимо заполнить таблицу

        Выводной параметр:
        bool: True - все ключи словаря my_dict соответствуют col_list, False - наоборот
        """

        # Вывод ключей словаря
        dict_keys = [k for k, _ in dict_user.items()]

        # Проверка наличия всех нужных ключей словаря dict_user относительно списка col_list
        for dict_key in dict_keys:
            if dict_key not in col_list:
                print(f'Ключ {dict_key} не найден в следующем словаре: {dict_user}')
                return False

        return True


    def check_columns_type(self, col_types_list:list, dict_user:dict) -> bool:

        """
        Проверяет наличие корректных типов данных в столбцах.

        Вводные параметры:
        - col_types_list: список типов, указанных при составлении ORM классов
        - dict_user: словарь, содержащий значения конкретной таблицы

        Выводной параметр:
        bool: True - все значения соответствуют указанным типам данных, False - наоборот
        """

        type_dict = {
            'INTEGER': int,
            'VARCHAR': str,
            'BOOLEAN': bool
        }

        col_vals_list = [v for _, v in dict_user.items()]
        for col_type, col_val in zip(col_types_list, col_vals_list):

            type_name = []
            for type_key, _ in type_dict.items():
                if type_key in str(col_type):
                    type_name.append(type_key)

            if type_name:
                type_name = type_name[0]

                if type(col_val) is type_dict[type_name]:
                    pass

                else:
                    try:
                        raise TypeError(f"type({col_val}) != {type_name}")

                    except(TypeError) as e:
                        print('Ошибка ввода типа данных.', e, sep='\n')
                        return False

            else:
                print(f'Не учтен следующий тип данных: {str(col_type)}')

        return True


    def get_table_values(self, class_object:object) -> list[dict]:

        """
        Выводит значения таблицы по объекту класса, прикрепленного к данной таблице

        Вводимые параметры:
        - class_object: объект класса, отвечающего за конкретную таблицу

        Выводимый параметр:
        - data_list: список словарей, содержащих значения таблицы
        """

        engine = self.get_engine()
        session_class = sessionmaker(bind=engine)
        session = session_class()

        # Название столбцов таблицы Users
        col_list, _ = get_class_cols(class_object)

        try:
            # Попытка запуска запроса на получение данных
            query = session.query(class_object).all()

            # Попытка получения данных конкретной таблицы
            data_list = []
            for obj in query:
                data_dict = {}
                for col in col_list:
                    column_value = getattr(obj, col)
                    data_dict[col] = column_value
                data_list.append(data_dict)
            return data_list

        except (errors.UndefinedTable,
                exc.ProgrammingError) as e:
            print(f'Ошибка вызова таблицы.')
            print('Описание ошибки:', e, sep='\n')
            pass


    def do_autoincriment(self, dict_user:dict, class_object:object) -> dict:

        """
        Проводит автоинкримент в отношении данных, содержащихся в dict_user

        Вводимые параметры:
        - dict_user: словарь, содержащий значения конкретной таблицы
        - class_object: класс, относящийся к конкретной таблице

        Выводимые параметры:
        - dict_user: обновленный словарь, учитывающий автоинкримент
        """

        # Инициации сессии по вызову таблицы, принадлежащей к объекту класса class_object
        get_table_result = self.get_table_values(class_object)

        if get_table_result:
            new_id = get_table_result[-1].get('id') + 1
        else:
            new_id = 1

        dict_user.update({'id': new_id})
        return dict_user


    def add_user(self, list_dict:list[dict]) -> list[dict]:

        """
        Добавляет пользователя в таблицу users

        Вводной параметр:
        - list_dict: список словарей с данными пользователя (таблица users)

        Выводной параметр:
        - list[dict]: список словарей, содержащий данные таблицы users
        """

        for dict_user in list_dict:

            # Название столбцов таблицы users
            col_list, col_types_list = get_class_cols(Users)

            # Проверка cоответствия ключей dict_user названию столбцов из col_list
            if self.check_cols(col_list, dict_user):

                # Проверка cоответствия значений dict_user нужным типам данных
                if self.check_columns_type(col_types_list, dict_user):

                    # Запуск движка и инициация сессии
                    self.start_add_table_session(dict_user, Users)

        return self.get_table_values(Users)


    def get_favorites(self, user_id:int) -> list[dict]:

        """
        Выводит всех избранных пользователем людей (таблица favorites)

        Вводной параметр:
        - user_id: идентификатор пользователя ВК

        Выводной параметр:
        - list[dict]: список словарей, содержащий данные таблицы favorites
        """

        get_table_result = self.get_table_values(Favorites)

        if get_table_result:
            data = []
            for dict_data in get_table_result:
                id = dict_data.get('user_id', None)
                if id is not None and id == user_id:
                    data.append(dict_data)
            return data

        else:
            return []


    # Получение списка словарей для user_id
    def get_exceptions(self, user_id:int) -> list[dict]:

        """
        Выводит всех людей, находящихся в черном списке пользователя (таблица exceptions)

        Вводной параметр:
        - user_id: идентификатор пользователя ВК

        Выводной параметр:
        - list[dict]: список словарей, содержащий данные таблицы exceptions
        """

        get_table_result = self.get_table_values(Exceptions)

        if get_table_result:
            data = []
            for dict_data in get_table_result:
                id = dict_data.get('user_id', None)
                if id is not None and id == user_id:
                    data.append(dict_data)
            return data

        else:
            return []


    def add_favorites(self, list_dict:list[dict]) -> list[dict]:

        """
        Добавляет избранного человека в таблицу favorites

        Вводной параметр:
         - list_dict: список словарей с данными (таблица favorites)

        Выводной параметр:
        - list[dict]: список словарей, содержащий данные таблицы favorites
        """

        # Название столбцов таблицы favorites
        col_list, col_types_list = get_class_cols(Favorites)

        for dict_user in list_dict:

            # Проверка cоответствия ключей dict_user названию столбцов из col_list
            if self.check_cols(col_list, dict_user):

                # Проверка cоответствия значений dict_user нужным типам данных
                if self.check_columns_type(col_types_list, dict_user):

                    # user_id - пользователь, profile - профиль второй половинки
                    user_id = dict_user.get('user_id')
                    profile = dict_user.get('profile')

                    # Проверка наличия пары "Пользователь - Вторая половинка" в таблице favorites
                    search_result = self.get_favorites(user_id)
                    repeat_list = [dict_pair for dict_pair in search_result if dict_pair.get('profile') == profile]

                    # Учет отсутствия поаторов в паре "Пользователь - Вторая половинка"
                    if not repeat_list:

                        # Проведение автоинкримента (в данном случае он нужен, т.к. учитываются ID наблюдения)
                        dict_user = self.do_autoincriment(dict_user, Favorites)

                        # Запуск движка и инициация сессии
                        self.start_add_table_session(dict_user, Favorites)

                    else:
                        print('Указанная пара "Пользователь - Логин второй половинки" уже указана в таблице')

        return self.get_table_values(Favorites)


    # Добавление человека в черный список
    def add_exceptions(self, list_dict:list[dict]) -> list[dict]:

        """
        Добавляет человека в черный список (таблица exceptions)

        Вводной параметр:
        - list_dict: список словарей с данными (таблица exceptions)

        Выводной параметр:
        - list[dict]: список словарей, содержащий данные таблицы exceptions
        """

        # Название столбцов таблицы exceptions
        col_list, col_types_list = get_class_cols(Exceptions)

        for dict_user in list_dict:

            # Проверка cоответствия ключей dict_user названию столбцов из col_list
            if self.check_cols(col_list, dict_user):

                # Проверка cоответствия значений dict_user нужным типам данных
                if self.check_columns_type(col_types_list, dict_user):

                    # user_id - пользователь, profile - профиль второй половинки
                    user_id = dict_user.get('user_id')
                    profile = dict_user.get('profile')

                    # Проверка наличия пары "Пользователь - Вторая половинка" в таблице favorites
                    search_result = self.get_exceptions(user_id)
                    repeat_list = [dict_pair for dict_pair in search_result if dict_pair.get('profile') == profile]

                    # Учет отсутствия поаторов в паре "Пользователь - Вторая половинка"
                    if not repeat_list:

                        # Проведение автоинкримента (в данном случае он нужен, т.к. учитываются ID наблюдения)
                        dict_user = self.do_autoincriment(dict_user, Exceptions)

                        # Запуск движка и инициация сессии
                        self.start_add_table_session(dict_user, Exceptions)

                    else:
                        print('Указанная пара "Пользователь - Логин второй половинки" уже указана в таблице')

        return self.get_table_values(Exceptions)


    def delete_favorites(self, list_dict:list[dict]) -> list[dict]:

        """
        Удаляет человека из избранного списка пользователя (таблица favorites)

        Вводной параметр:
         - list_dict: список словарей с данными (таблица favorites)

        Выводной параметр:
        - list[dict]: список словарей, содержащий данные таблицы favorites
        """

        # Запуск движка
        engine = self.get_engine()

        for dict_user in list_dict:

            # Получения ID пользователя ВК и профиля
            user_id = dict_user.get('user_id')
            profile = {k: v for k, v in dict_user.items() if k != 'id'}.get('profile')

            # Инициация сессии
            session_class = sessionmaker(bind=engine)
            session = session_class()

            try:
                # Формирование запроса
                delete_query = session.query(Favorites). \
                    where(and_(Favorites.profile == profile,
                               Favorites.user_id == user_id)).all()

            except (errors.UndefinedFunction,
                    sqlalchemy.exc.ProgrammingError,
                    errors.NumericValueOutOfRange,
                    sqlalchemy.exc.DataError):
                delete_query = []

            # Условие наличия запроса
            if delete_query:
                for query in delete_query:
                    # Удаление данных и завершение сессии
                    session.delete(query)
                    session.commit()
                    session.close()

        return self.get_table_values(Favorites)


    def delete_exceptions(self, list_dict:list[dict]) -> list[dict]:

        """
        Удаляет человека из черного списка пользователя (таблица exceptions)

        Вводной параметр:
         - list_dict: список словарей с данными (таблица exceptions)

        Выводной параметр:
        - list[dict]: список словарей, содержащий данные таблицы exceptions
        """

        # Запуск движка
        engine = self.get_engine()

        for dict_user in list_dict:

            # Получения ID пользователя ВК и профиля
            user_id = dict_user.get('user_id')
            profile = {k: v for k, v in dict_user.items() if k != 'id'}.get('profile')

            # Инициация сессии
            session_class = sessionmaker(bind=engine)
            session = session_class()

            try:
                # Формирование запроса
                delete_query = session.query(Exceptions). \
                    where(and_(Exceptions.profile == profile,
                               Exceptions.user_id == user_id)).all()

            except (errors.UndefinedFunction,
                    sqlalchemy.exc.ProgrammingError,
                    errors.NumericValueOutOfRange,
                    sqlalchemy.exc.DataError):
                delete_query = []

            # Условие наличия запроса
            if delete_query:
                for query in delete_query:
                    # Удаление данных и завершение сессии
                    session.delete(query)
                    session.commit()
                    session.close()

        return self.get_table_values(Exceptions)