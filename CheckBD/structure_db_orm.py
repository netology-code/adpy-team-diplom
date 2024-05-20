import sys
import inspect

import sqlalchemy as sq
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Genders(Base):
    """
    Наименование таблицы:
    - genders

    Столбцы:
    - id: ID пола
    - gender: наименование пола
    """

    __tablename__ = 'genders'

    id = sq.Column(
        sq.Integer,
        primary_key=True
    )

    gender = sq.Column(
        sq.String(length=10),
        nullable=False,
        unique=True
    )


class Cities(Base):
    """
    Наименование таблицы:
    - cities

    Столбцы:
    - id: ID города
    - name: наименование города
    """

    # искать по названию в ВК (пока непонятно)
    __tablename__ = 'cities'

    id = sq.Column(
        sq.Integer,
        primary_key=True
    )

    name = sq.Column(
        sq.String(length=50),
        nullable=False,
        unique=True
    )


class Users(Base):
    """
    Название таблицы:
    - users

    Столбцы:
    - id: уникальный ID пользователя приложения (ID ВК)
    - first_name: имя пользователя
    - last_name: фамилия пользователя
    - age: возраст пользователя
    - gender_id: ID пола пользователя (FK1: genders.id)
    - city_id: ID города проживания пользователя (FK2: cities.id)
    - about_me: информация о пользователе
    """

    __tablename__ = 'users'

    id = sq.Column(
        sq.Integer,
        primary_key=True
    )

    first_name = sq.Column(
        sq.String(length=50),
        nullable=False
    )

    last_name = sq.Column(
        sq.String(length=50),
        nullable=False
    )

    age = sq.Column(
        sq.Integer,
        nullable=False
    )

    gender_id = sq.Column(
        sq.Integer,
        sq.ForeignKey('genders.id'),
        nullable=False
    )

    city_id = sq.Column(
        sq.Integer,
        sq.ForeignKey('cities.id'),
        nullable=False
    )

    about_me = sq.Column(
        sq.String(length=1500),
        nullable=False
    )


class Criteria(Base):
    """
    Наименование таблицы:
    - criteria

    Столбцы:
    - id: ID критерия поиска
    - user_id: ID пользователя ВК
    - gender_id: ID пола пользователя
    - status: статус (женат, холост и т.д.)
    - age_from: начальный возраст партнера
    - age_to: конечеый возраст партнера
    - city_id: ID города пользователя
    - has_photo: факт наличия фото
      (1 - есть фото, 0 - фото отсутствует)
    """

    __tablename__ = 'criteria'

    id = sq.Column(
        sq.Integer,
        primary_key=True
    )

    user_id = sq.Column(
        sq.Integer,
        sq.ForeignKey('users.id',
                      ondelete='CASCADE'),
        nullable=False
    )

    gender_id = sq.Column(
        sq.Integer,
        nullable=False
    )

    status = sq.Column(
        sq.Integer,
        nullable=False
    )

    age_from = sq.Column(
        sq.Integer,
        nullable=False
    )

    age_to = sq.Column(
        sq.Integer,
        nullable=False
    )

    city_id = sq.Column(
        sq.Integer,
        nullable=False
    )

    has_photo = sq.Column(
        sq.Integer,
        nullable=False
    )


class Favorites(Base):
    """
    Название таблицы:
    - favorites

    Столбцы:
    - id: уникальный ID пары "пользователь-вторая половинка"
    - user_id: уникальный ID пользователя приложения (FK1: users.id)
    - first_name: имя второй половинки
    - last_name: фамилия второй половинки
    - age: возраст второй половинки
    - gender_id: пол второй половинки (FK2: genders.id)
    - profile: наименование профиля второй половинки
    - photo1: ссылка на первый рисунок второй половинки
    - photo2: ссылка на второй рисунок второй половинки
    - photo3: ссылка на третий рисунок второй половинки
    - city_id: ID города проживания пользователя (FK3: cities.id)
    """

    __tablename__ = 'favorites'

    id = sq.Column(
        sq.Integer,
        primary_key=True
    )

    user_id = sq.Column(
        sq.Integer,
        sq.ForeignKey('users.id',
                      ondelete='CASCADE'),
        nullable=False
    )

    first_name = sq.Column(
        sq.String(length=50),
        nullable=False
    )

    last_name = sq.Column(
        sq.String(length=50),
        nullable=False
    )

    age = sq.Column(
        sq.Integer,
        nullable=False
    )

    gender_id = sq.Column(
        sq.Integer,
        sq.ForeignKey('genders.id'),
        nullable=False
    )

    profile = sq.Column(
        sq.String(length=50),
        nullable=False
    )

    photo1 = sq.Column(
        sq.String(length=1000),
    )

    photo2 = sq.Column(
        sq.String(length=1000),
    )

    photo3 = sq.Column(
        sq.String(length=1000),
    )

    city_id = sq.Column(
        sq.Integer,
        sq.ForeignKey('cities.id'),
        nullable=False
    )


class Exceptions(Base):
    """
    Название таблицы:
    - exceptions

    Столбцы:
    - id: уникальный ID пары "пользователь-вторая половинка"
    - first_name: имя второй половинки
    - last_name: фамилия второй половинки
    - user_id: уникальный ID пользователя приложения (FK1: users.id)
    - age: возраст второй половинки
    - gender_id: пол второй половинки (FK2: genders.id)
    - profile: наименование профиля второй половинки
    - photo1: ссылка на первый рисунок второй половинки
    - photo2: ссылка на второй рисунок второй половинки
    - photo3: ссылка на третий рисунок второй половинки
    - city_id: ID города проживания пользователя (FK3: cities.id)
    """

    __tablename__ = 'exceptions'

    id = sq.Column(
        sq.Integer,
        primary_key=True
    )

    user_id = sq.Column(
        sq.Integer,
        sq.ForeignKey('users.id',
                      ondelete='CASCADE'),
        nullable=False
    )

    first_name = sq.Column(
        sq.String(50),
        nullable=False
    )

    last_name = sq.Column(
        sq.String(length=50),
        nullable=False
    )

    age = sq.Column(
        sq.Integer,
        nullable=False
    )

    gender_id = sq.Column(
        sq.Integer,
        sq.ForeignKey('genders.id'),
        nullable=False
    )

    profile = sq.Column(
        sq.String(50),
        nullable=False
    )

    photo1 = sq.Column(
        sq.String(1000),
    )

    photo2 = sq.Column(
        sq.String(1000),
    )

    photo3 = sq.Column(
        sq.String(1000),
    )

    city_id = sq.Column(
        sq.Integer,
        sq.ForeignKey('cities.id'),
        nullable=False
    )


# Создание таблиц в БД
def form_tables(engine):
    """
    Назначение: создание таблиц в БД

    Вводной параметр:
    - engine: движок, формируемый в результате
    отработки функции sqlalchemy.create_engine()
    """

    Base.metadata.create_all(engine)
