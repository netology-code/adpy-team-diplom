import random

from sqlalchemy import exists, exc
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from db.create_db import Users, Partner, Favorite, Blacklist
from db.create_db import create_tables


class ORMvk:
    def __init__(self, engine):
        self.engine = engine

    def create_session_db(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    '''
    Проверяет наличие БД  и при необходимости создает базу и таблицы
    '''

    def check_database(self):
        if not database_exists(self.engine.url):
            create_database(self.engine.url)
        create_tables(self.engine)
        self.engine.dispose()
        print('База данных созданна')

    def get_user_id(self, vk_id):
        session = self.create_session_db()
        with session.begin():
            user = session.query(Users).filter(Users.vk_id == vk_id).first()
            if user is not None:
                return user.user_id

    def add_user(self, vk_id, data):
        session = self.create_session_db()
        user = session.query(Users).filter(Users.vk_id == vk_id).first()
        if user is None:
            new_user = Users(vk_id=vk_id)
            session.add(new_user)
            session.commit()
            user = session.query(Users).filter(Users.vk_id == vk_id).first()
        for key, value in data.items():
            setattr(user, key, value)
        session.commit()
        session.close()
        self.engine.dispose()

    # data - словарь содержащий информацию о партнере
    def add_partner(self, user_vk_id, partner_vk_id, data):
        session = self.create_session_db()
        partner = session.query(Partner).filter(Partner.partner_vk_id == partner_vk_id).first()
        user = session.query(Users).filter(Users.vk_id == user_vk_id).first()
        if partner is None:
            new_partner = Partner(partner_vk_id=partner_vk_id, user_id=user.user_id)
            session.add(new_partner)
            session.commit()
            partner = session.query(Partner).filter(Partner.partner_vk_id == partner_vk_id).first()
        partner.user_id = user.user_id
        for key, value in data.items():
            setattr(partner, key, value)
        session.commit()
        session.close()
        self.engine.dispose()

    def add_blacklist(self, partner_id):
        session = self.create_session_db()
        with session.begin():
            partner = session.query(Partner).filter(Partner.partner_id == partner_id).first()
            blocked = session.query(Blacklist).filter(Blacklist.partner_id == partner_id).first()

            if blocked is None:
                new_blocked = Blacklist(user_id=partner.user_id, partner_id=partner_id)
                session.add(new_blocked)
                session.commit()

    def get_blacklist(self, user_id):
        session = self.create_session_db()
        with session.begin():
            blacklist = session.query(Blacklist).filter(Blacklist.user_id == user_id).all()
            if blacklist is not None:
                return [item.partner_id for item in blacklist]

    def add_favorite(self, partner_id):
        session = self.create_session_db()
        with session.begin():
            partner = session.query(Partner).filter(Partner.partner_id == partner_id).first()
            favorite = session.query(Favorite).filter(Favorite.partner_id == partner_id).first()

            if favorite is None:
                new_favorite = Favorite(user_id=partner.user_id, partner_id=partner_id)
                session.add(new_favorite)
                session.commit()

    def get_favorite_list(self, user_id):
        session = self.create_session_db()
        with session.begin():
            favorite_list = session.query(Favorite).filter(Favorite.user_id == user_id).all()
            if favorite_list is not None:
                return [item.partner_id for item in favorite_list]

    def get_random_partner(self):
        session = self.create_session_db()
        with session.begin():
            subblack = exists().where(Blacklist.partner_id == Partner.partner_id)
            subfavor = exists().where(Favorite.partner_id == Partner.partner_id)
            query = session.query(Partner).filter(~subblack).filter(~subfavor)
            random_row = query.offset(int(int(query.count()) * random.random())).limit(1).scalar()
            if random_row is not None:
                session.query(Users).filter(Users.user_id == random_row.user_id). \
                    update({"last_id": random_row.partner_id})

                return random_row.name, random_row.surname, random_row.link, random_row.foto

    def get_partner(self, partner_id):
        session = self.create_session_db()
        with session.begin():
            partner = session.query(Partner).get(partner_id)
            if partner is not None:
                return partner.name, partner.surname, partner.link, partner.foto

    def get_search_data(self, vk_id):
        session = self.create_session_db()
        with session.begin():
            user = session.query(Users).filter(Users.vk_id == vk_id).first()
            if user is not None:
                if user.gender == 2:
                    gender = 1
                else:
                    gender = 2

                return user.age, gender, user.city

    def get_last_user_id(self, user_id):
        session = self.create_session_db()
        with session.begin():
            user = session.query(Users).filter(Users.user_id == user_id).scalar()
            if user is not None:
                return user.last_id

    def add_state(self, user_vk_id, state):
        session = self.create_session_db()
        with session.begin():
            user = session.query(Users).filter(Users.user_vk_id == user_vk_id).first()
            if user is not None:
                session.query(Users).filter(Users.user_id == user.user_id). \
                        update({"state": state})

    def get_state(self, user_vk_id):
        session = self.create_session_db()
        with session.begin():
            user = session.query(Users).filter(Users.user_vk_id == user_vk_id).first()
            if user is not None:
                return user.state

    def add_offset(self, user_vk_id, offset):
        session = self.create_session_db()
        with session.begin():
            user = session.query(Users).filter(Users.user_vk_id == user_vk_id).first()
            if user is not None:
                session.query(Users).filter(Users.user_id == user.user_id). \
                        update({"offset": offset})

    def get_offset(self, user_vk_id):
        session = self.create_session_db()
        with session.begin():
            user = session.query(Users).filter(Users.user_vk_id == user_vk_id).first()
            if user is not None:
                return user.offset

    def clear_table(self):
        session = self.create_session_db()
        try:
            session.query(Partner).delete()
            session.commit()
        except exc.SQLAlchemyError:
            session.rollback()
        session.close()
        self.engine.dispose()

    def clear_partner_row(self, user_id):
        session = self.create_session_db()
        with session.begin():
            user = session.query(Users).filter(Users.user_id == user_id).first()
            if user is not None:
                session.query(Partner).filter(Partner.partner_id == user.last_id).delete()
                session.query(Users).filter(Users.user_id == user_id).update({"last_id": None})
                session.commit()
