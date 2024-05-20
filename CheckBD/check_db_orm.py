import os

import sqlalchemy as sq
from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_utils import database_exists, create_database

from CheckBD.ABCCheckDb import ABCCheckDb
from CheckBD.structure_db_orm import form_tables, Genders


class CheckDBORM(ABCCheckDb):

    def get_engine(self) -> Engine:
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

    def start_session(self) -> Session:
        """
        Инициирует сессию

        Выводной параметр:
        - экземпляр класса Session
        """

        engine = self.get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()
        return session

    def exists_db(self) -> bool:
        """
        Проверяет наличие БД в Postgres

        Выводимый параметр:
        bool : True - есть база данных, False - нет базы данных
        """

        engine = self.get_engine()

        if not database_exists(engine.url):
            return False
        else:
            return True

    def create_db(self) -> None:
        """
        Создает базу данных
        """

        engine = self.get_engine()

        if not self.exists_db():
            create_database(engine.url)

    def exists_tables(self, table_name: str) -> bool:
        """
        Проверяет существование таблицы в БД

        Вводной параметр:
        - table_name: наименование таблицы

        Выводимый параметр:
        bool : True -таблица есть в БД,
               False - таблица отсутствует в БД
        """

        engine = self.get_engine()

        if not sq.inspect(engine).has_table(table_name):
            return False
        else:
            return True

    def create_tables(self):
        """
        Создает таблицы в БД
        """

        engine = self.get_engine()
        form_tables(engine)

        for name_table in self.tables:
            if not self.exists_tables(name_table):
                self.error = 'Не все таблицы созданы'

    def fill_tables(self):
        """
        Заполняет таблицу genders
        """

        session = self.start_session()
        genders = session.query(Genders).all()

        if not genders:
            female = Genders(
                id=1,
                gender='Женщина'
            )
            male = Genders(
                id=2,
                gender='Мужчина'
            )
            session.add_all([
                female,
                male
            ])
            session.commit()

        session.close()
