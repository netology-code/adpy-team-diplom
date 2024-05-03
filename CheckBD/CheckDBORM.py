import os
from dotenv import load_dotenv

import sqlalchemy as sq
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from ORMTableStructure import form_tables, get_table_list
from CheckBD.ABCCheckDb import ABCCheckDb



class CheckDBORM(ABCCheckDb):

    def get_engine(self):

        """
        Формирует движок Sqlalchemy

        Выводной параметр:
        - движок Sqlalchemy
        """

        load_dotenv()

        dbname = 'findme'
        user = os.getenv(key='USER_NAME_DB')
        password = os.getenv(key='USER_PASSWORD_DB')
        host = 'localhost'
        port = '5432'

        dns_link = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        return create_engine(dns_link)


    def exists_db(self):

        """
        Проверяет наличие БД в Postgres

        Вводимый параметр:
        engine - движок Sqlalchemy

        Выводимый параметр:
        bool : True - есть база данных, False - нет базы данных
        """

        engine = self.get_engine()

        if not database_exists(engine.url):
            return False
        else:
            return True


    def create_db(self):

        """
        Создает базу данных

        Вводимый параметр:
        engine - движок Sqlalchemy

        Выводимый параметр:
        bool : True - есть база данных, False - нет базы данных
        """

        engine = self.get_engine()

        if not self.exists_db():
            create_database(engine.url)


    def exists_tables(self):

        """
        Проверяет существование таблиц в БД

        Вводимый параметр:
        engine - движок Sqlalchemy

        Выводимый параметр:
        bool : True - все таблицы есть в БД, False - не все таблицы имеются в БД
        """

        engine = self.get_engine()
        table_list = get_table_list()

        for table_name in table_list:
            if not sq.inspect(engine).has_table(table_name):
                return False
        return True


    def create_tables(self):

        """
        Создает таблицы в БД в случае их отсутствия

        Вводимый параметр:
        engine - движок Sqlalchemy
        """

        engine = self.get_engine()

        if not self.exists_tables():
            form_tables(engine)


    def fill_tables(self):
        pass