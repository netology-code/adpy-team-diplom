import sqlalchemy
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from models import create_tables,USERS,PRETENDENTS,FAVOURITES
from pprint import pprint


DSN = f'postgresql://postgres:masterkey@localhost:5432/vk_db' # Строка подключения к базе данных
engine = sqlalchemy.create_engine(DSN)

# create_tables(engine) # Эта функция создает/пересоздает таблицы. Для создания необходимо раскомментировать, потом закомментировать. Иначе таблицы будут пересоздаваться каждый раз.

Session = sessionmaker(bind=engine)
session = Session()


def users_insert(id_vk: int, first_name: str, last_name: str, city: str, age: int, sex: int):
    '''Функция вставляет в таблицу USERS поля: id_vk-пользователя, фамилию, имя, город, возраст, пол.
    id_vk всегда уникальны.
    '''
    values_ = USERS(id_vk = id_vk, first_name = first_name, last_name = last_name, city = city, age = age, sex = sex)
    session.add(values_)
    session.commit()


def pretendents_insert(id_vk: int, id_vk_pret: int, first_name: str, last_name: str,  photo_1: str, photo_2: str, photo_3: str):
    '''
    Сначала функция по id_vk находит в таблице USERS id пользователя (это нужно чтобы связать пользователя и претендента), затем
    вставляет в таблицу PRETENDENTS поля: id_user (это поле id из таблицы USERS), id_vk_pret, фамилию, имя, ссылки на фото.
    '''
    for users in session.query(USERS).filter(USERS.id_vk == id_vk):
        id_user = users.id

    values_ = PRETENDENTS(id_user = id_user, id_vk_pret = id_vk_pret, first_name = first_name, last_name = last_name, photo_1 = photo_1, photo_2 = photo_2, photo_3 = photo_3)
    session.add(values_)
    session.commit()


def favourites_insert(id_vk: int, id_vk_fav: int, first_name: str, last_name: str,  photo_1: str, photo_2: str, photo_3: str):
    '''
    Сначала функция по id_vk находит в таблице USERS id пользователя (это нужно чтобы связать пользователя и избранного), затем
    вставляет в таблицу FAVOURITES поля: id_user (это поле id из таблицы USERS), id_vk_fav, фамилию, имя, ссылки на фото.
    '''
    for users in session.query(USERS).filter(USERS.id_vk == id_vk):
        id_user = users.id

    values_ = FAVOURITES(id_user = id_user, id_vk_fav = id_vk_fav, first_name = first_name, last_name = last_name, photo_1 = photo_1, photo_2 = photo_2, photo_3 = photo_3)
    session.add(values_)
    session.commit()


def pretendents_output(id_vk: int):
    '''Функция на вход принимает id_vk пользователя. Функция возращает словарь, где id_vk претендента - ключ, а  фамилия, имя, и ссылки на фото - элементы списка в значении словаря.'''
    pretendents_ = []
    for pretendents in session.query(PRETENDENTS).join(USERS).filter(USERS.id_vk == id_vk).all():
        list_= [pretendents.id_vk_pret, pretendents.first_name, pretendents.last_name, pretendents.photo_1, pretendents.photo_2, pretendents.photo_3]
        pretendents_.append(list_)
    return pretendents_


def favourites_output(id_vk: int):
    '''Функция на вход принимает id_vk пользователя. Функция возращает словарь, где id_vk избранного - ключ, а  фамилия, имя, и ссылки на фото - элементы списка в значении словаря.'''
    favourites_ = []
    for favourite in session.query(FAVOURITES).join(USERS).filter(USERS.id_vk == id_vk).all():
        list_ = [favourite.id_vk_fav, favourite.first_name, favourite.last_name, favourite.photo_1, favourite.photo_2, favourite.photo_3]
        favourites_.append(list_)
    return favourites_


def vk_users_param_output(id_vk: int):
    '''Функция на вход принимает id_vk пользователя. Функция возращает город,возраст, пол пользователя.
    Не знаю, нужна ли эта функция вообще...Может пригодиться когда делается запрос по параметрам'''
    for users in session.query(USERS).filter(USERS.id_vk == id_vk):
        return users.city,users.age,users.sex

session.close()