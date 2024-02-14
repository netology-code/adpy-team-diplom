import random

from sqlalchemy import exists, exc, select, update
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, create_database

from db.create_db import Users, Partner, Favorite, Blacklist
from db.create_db import create_tables


class ORMvk:
    def __init__(self, engine):
        self.engine = engine
        self.session = Session(engine)

    '''
    Проверяет наличие БД  и при необходимости создает базу и таблицы
    '''
    def check_database(self):
        if not database_exists(self.engine.url):
            create_database(self.engine.url)
        create_tables(self.engine)
        self.engine.dispose()
        print('База данных созданна')

    ''' Возвращает ID пользователя'''
    def get_user_id(self, vk_id) -> int:
        q = select(Users).where(Users.vk_id == vk_id)
        with self.session as session:
            user = session.execute(q).scalar()
        if user is not None:
            return user.user_id

    '''Добавляет нового пользоавтеля в таблицу БД.'''
    def add_user(self, vk_id, data):
        if self.session is not None:
            q = select(Users).where(Users.vk_id == vk_id)
            new_user = Users(vk_id=vk_id)
            with self.session as session:
                user = session.execute(q).scalar()
            if user is None:
                session.add(new_user)
                session.commit()
                user = session.execute(q).scalar()
            for key, value in data.items():
                setattr(user, key, value)
            session.commit()

    '''Добавляет партнера в таблицу БД'''
    def add_partner(self, user_vk_id, partner_vk_id, data):
        partner_q = select(Partner).where(Partner.partner_vk_id == partner_vk_id)
        user_q = select(Users).where(Users.vk_id == user_vk_id)

        with self.session as session:
            partner = session.execute(partner_q).scalar()
            user = session.execute(user_q).scalar()

        if partner is None:
            new_partner = Partner(partner_vk_id=partner_vk_id, user_id=user.user_id)
            with self.session as session:
                session.add(new_partner)
                session.commit()
                partner = session.execute(partner_q).scalar()
                partner.user_id = user.user_id
                for key, value in data.items():
                    setattr(partner, key, value)
                session.commit()

    '''Добавляет партнера в блэк-лист'''
    def add_blacklist(self, partner_id):
        partner_q = select(Partner.user_id).where(Partner.partner_id == partner_id)
        blocked_q = select(Blacklist).where(Blacklist.partner_id == partner_id)
        with self.session as session:
            partner = session.execute(partner_q).scalar()
            blocked = session.execute(blocked_q).scalar()

            if blocked is None:
                new_blocked = Blacklist(user_id=partner, partner_id=partner_id)
                session.add(new_blocked)
                session.commit()

    '''Возвращает список заблокированных пользователей'''
    def get_blacklist(self, user_id) -> list:
        q = select(Blacklist).where(Blacklist.user_id == user_id)
        with self.session as session:
            blacklist = session.execute(q).all()
        if blacklist is not None:
            return [item.partner_id for items in blacklist for item in items]

    '''Добавляет партнера в избранное'''
    def add_favorite(self, partner_id):
        partner_q = select(Partner.user_id).where(Partner.partner_id == partner_id)
        favorite_q = select(Favorite).where(Favorite.partner_id == partner_id)
        with self.session as session:
            partner = session.execute(partner_q).scalar()
            favorite = session.execute(favorite_q).scalar()
        if favorite is None:
            new_favorite = Favorite(user_id=partner, partner_id=partner_id)
            with self.session as session:
                session.add(new_favorite)
                session.commit()

    '''Возвращает список пользователей в избранном'''
    def get_favorite_list(self, user_id):
        q = select(Favorite).where(Favorite.user_id == user_id)
        with self.session as session:
            favorite_list = session.execute(q).all()
        if favorite_list is not None:
            return [item.partner_id for items in favorite_list for item in items]

    '''Возвращает случайного партнера из БД'''
    def get_random_partner(self) -> any:
        # session = self.create_session_db()
        subblack = exists().where(Blacklist.partner_id == Partner.partner_id)
        subfavor = exists().where(Favorite.partner_id == Partner.partner_id)
        with self.session as session:
            query = session.query(Partner).filter(~subblack).filter(~subfavor)
            random_row = query.offset(int(int(query.count()) * random.random())).limit(1).scalar()
            if random_row is not None:
                q = update(Users).where(Users.user_id == random_row.user_id).values(last_id=random_row.partner_id)
                session.execute(q)
                session.commit()

                return random_row.name, random_row.surname, random_row.link, random_row.foto

    '''Возвращает информацию о партнере'''
    def get_partner(self, partner_id):
        q = select(Partner).where(Partner.partner_id == partner_id)
        with self.session as session:
            partner = session.execute(q).scalar()
        if partner is not None:
            return partner.name, partner.surname, partner.link, partner.foto

    def get_search_data(self, vk_id):
        q = select(Users).where(Users.vk_id == vk_id)
        with self.session as session:
            user = session.execute(q).scalar()
        if user is not None:
            if user.gender == 2:
                gender = 1
            else:
                gender = 2

            return user.age, gender, user.city

    '''Служебная. Возвращает последнего просмотренного партнера'''
    def get_last_user_id(self, user_id) -> int:
        q = select(Users).where(Users.user_id == user_id)
        with self.session as session:
            user = session.execute(q).scalar()
            if user is not None:
                return user.last_id

    '''Служебная. Добавляет состояние бота'''
    def add_state(self, user_vk_id, state):
        with self.session as session:
            session.connection().execute(
                update(Users).where(Users.vk_id == user_vk_id),
                {"state": state}
            )
            session.commit()

    '''Служебная. Возвращает состояние бота для пользователя'''
    def get_state(self, user_vk_id) -> int:
        q = select(Users).where(Users.vk_id == user_vk_id)
        with self.session as session:
            user = session.execute(q).scalar()
            if user is not None:
                return user.state

    '''Служебная. Удаление таблиц'''
    def clear_table(self):
        with self.session as session:
            try:
                session.query(Partner).delete()
                session.commit()
            except exc.SQLAlchemyError:
                session.rollback()

    '''Служебная. Удаляет партнера из БД'''
    def clear_partner_row(self, user_id):
        with self.session as session:
            user = session.query(Users).filter(Users.user_id == user_id).first()
            if user is not None:
                session.query(Partner).filter(Partner.partner_id == user.last_id).delete()
                session.query(Users).filter(Users.user_id == user_id).update({"last_id": None})
                session.commit()

    def clear_partner_all(self, user_id):
        subblack = exists().where(Blacklist.partner_id == Partner.partner_id)
        subfavor = exists().where(Favorite.partner_id == Partner.partner_id)

        with self.session as session:
            session.query(Partner).filter(Partner.user_id == user_id).filter(~subblack).filter(~subfavor).delete()
            session.commit()