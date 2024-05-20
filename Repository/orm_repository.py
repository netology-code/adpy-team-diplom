import os
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session

from user import User
from Repository.card_favorites import CardFavorites
from Repository.card_exceptions import CardExceptions
from Repository.abc_repository import ABCRepository
from CheckBD.structure_db_orm import Users, Cities, Criteria, Favorites, Exceptions


class ORMRepository(ABCRepository):

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

    def add_user(self, user: User) -> None:
        """
        Добавляет или обновляет пользователя в БД

        Вводной параметр:
        - user: экземпляр класса User
        """

        session = self.start_session()
        user_query = session.query(Users). \
            filter(Users.id == user.get_user_id()). \
            first()

        if user_query:
            user_query.first_name = user.get_first_name()
            user_query.last_name = user.get_last_name()
            user_query.age = user.get_age()
            user_query.gender_id = user.get_gender()
            user_query.city_id = user.get_city()['id']
            user_query.about_me = user.get_about_me()
            session.commit()

        else:
            city_query = session.query(Cities). \
                filter(Cities.name == user.get_city()['name']). \
                first()

            if not city_query:
                new_city = Cities(
                    id=user.get_city()['id'],
                    name=user.get_city()['name']
                )
                session.add(new_city)
                session.commit()

            new_user = Users(
                id=user.get_user_id(),
                first_name=user.get_first_name(),
                last_name=user.get_last_name(),
                age=user.get_age(),
                gender_id=user.get_gender(),
                city_id=user.get_city()['id'],
                about_me=user.get_about_me()
            )
            session.add(new_user)
            session.commit()

            all_criteria = session.query(Criteria). \
                all()
            if not all_criteria:
                new_id = 1
            else:
                new_id = len([item for item in all_criteria]) + 1

            new_criteria = Criteria(
                id=new_id,
                user_id=user.get_user_id(),
                gender_id=user.get_gender(),
                status=1,
                age_from=user.get_age() - 5,
                age_to=user.get_age() + 5,
                city_id=user.get_city()['id'],
                has_photo=1)
            session.add(new_criteria)
            session.commit()

        session.close()

    def add_favorites(self, user: User) -> None:
        """
        Добавляет партнера пользователя в таблицу favorites

        Вводной параметр:
        - user: экземпляр класса User
        """

        session = self.start_session()
        card = user.get_card()
        photos = card.photos

        profile = 'https://vk.com/id' + str(card.id)
        existing_favorite = session.query(Favorites).\
            filter_by(user_id=user.get_user_id(), profile=profile).\
            all()

        if not existing_favorite:
            favorites = session.query(Favorites).\
                all()
            if not favorites:
                new_id = 1
            else:
                new_id = len([item for item in favorites]) + 1

            new_favorite = Favorites(
                id=new_id,
                user_id=user.get_user_id(),
                first_name=card.first_name,
                last_name=card.last_name,
                age=card.age,
                gender_id=card.gender,
                profile=profile,
                photo1=photos[0] if photos else '',
                photo2=photos[1] if len(photos) > 1 else '',
                photo3=photos[2] if len(photos) > 2 else '',
                city_id=card.city_id
            )
            session.add(new_favorite)
            session.commit()

        existing_exception = session.query(Exceptions).\
            filter_by(user_id=user.get_user_id(), profile=profile).\
            all()
        session.close()

        if existing_exception:
            self.delete_exceptions(user_id=user.get_user_id(), profile=profile)

    def add_exceptions(self, user: User) -> None:
        """
        Добавляет партнера пользователя в таблицу exceptions

        Вводной параметр:
        - user: экземпляр класса User
        """

        session = self.start_session()
        card = user.get_card()
        photos = card.photos

        profile = 'https://vk.com/id' + str(card.id)
        existing_exception = session.query(Exceptions).\
            filter_by(user_id=user.get_user_id(), profile=profile).\
            all()

        if not existing_exception:
            exceptions = session.query(Exceptions).\
                all()
            if not exceptions:
                new_id = 1
            else:
                new_id = len([item for item in exceptions]) + 1

            new_exception = Exceptions(
                id=new_id,
                user_id=user.get_user_id(),
                first_name=card.first_name,
                last_name=card.last_name,
                age=card.age,
                gender_id=card.gender,
                profile='https://vk.com/id' + str(card.id),
                photo1=photos[0] if photos else '',
                photo2=photos[1] if len(photos) > 1 else '',
                photo3=photos[2] if len(photos) > 2 else '',
                city_id=card.city_id
            )
            session.add(new_exception)
            session.commit()

        existing_favorite = session.query(Favorites). \
            filter_by(user_id=user.get_user_id(), profile=profile). \
            all()
        session.close()

        if existing_favorite:
            self.delete_favorites(user_id=user.get_user_id(), profile=profile)

    def delete_favorites(self, user_id: int, profile: str) -> None:
        """
        Удаляет партнера пользователя из таблицы exceptions

        Вводные параметры:
        - user_id: VK ID пользователя приложения
        - profile: профиль партнера пользователя
        """

        session = self.start_session()
        existing_favorite = session.query(Favorites). \
            filter_by(user_id=user_id, profile=profile). \
            first()

        if existing_favorite:
            session.delete(existing_favorite)
            session.commit()

        session.close()

    def delete_exceptions(self, user_id: int, profile: str) -> None:
        """
        Удаляет партнера пользователя из таблицы exceptions

        Вводные параметры:
        - user_id: VK ID пользователя приложения
        - profile: профиль партнера пользователя
        """

        session = self.start_session()
        existing_exception = session.query(Exceptions). \
            filter_by(user_id=user_id, profile=profile). \
            first()

        if existing_exception:
            session.delete(existing_exception)
            session.commit()

        session.close()

    def get_favorites(self, user_id: int) -> Optional[list]:
        """
        Выводит список избранных партнеров по ID пользователя

        Вводной параметр:
        - user_id: VK ID пользователя приложения

        Вводные параметры:
        - list: список словарей с данными избранных партнеров
        """

        session = self.start_session()
        existing_favorites = session.query(Favorites, Cities).\
            join(Cities, Cities.id == Favorites.city_id).\
            filter(Favorites.user_id == user_id).\
            all()
        session.close()

        card_list = []
        if existing_favorites:
            for item, item2 in existing_favorites:
                card = CardFavorites()
                card.id = item.id
                card.first_name = item.first_name
                card.last_name = item.last_name
                card.age = item.age
                card.gender_id = item.gender_id
                card.profile = item.profile
                card.photos = [item.photo1, item.photo2, item.photo3]
                card.city_id = item2.id
                card.city_name = item2.name
                card_list.append(card)

        if len(card_list) > 0:
            return card_list
        else:
            return None

    def get_exceptions(self, user_id: int) -> Optional[list]:
        """
        Выводит список партнеров, включенных в черный список, по ID пользователя

        Вводной параметр:
        - user_id: VK ID пользователя приложения

        Вводные параметры:
        - list: список словарей с данными партнеров из черного списка
        """

        session = self.start_session()
        existing_exceptions = session.query(Exceptions, Cities).\
            join(Cities, Cities.id == Exceptions.city_id).\
            filter(Exceptions.user_id == user_id).\
            all()
        session.close()

        card_list = []
        if existing_exceptions:
            for item, item2 in existing_exceptions:
                card = CardExceptions()
                card.id = item.id
                card.first_name = item.first_name
                card.last_name = item.last_name
                card.age = item.age
                card.gender_id = item.gender_id
                card.profile = item.profile
                card.photos = [item.photo1, item.photo2, item.photo3]
                card.city_id = item2.id
                card.city_name = item2.name
                card_list.append(card)

        if len(card_list) > 0:
            return card_list
        else:
            return None

    def get_user(self, user_id: int) -> Optional[User]:
        """
        Выводит информацию о пользователе,
        содержащуюся в экземпляре класса User

        Вводимый параметр:
        - user_id: VK ID пользователя приложения

        Выводимый параметр:
        - User: наполненный экземпляр класса User
        """

        session = self.start_session()
        existing_user = session.query(Users, Cities).\
            join(Cities, Cities.id == Users.city_id).\
            filter(Users.id == user_id).\
            all()
        session.close()

        if existing_user:
            user = User(user_id)
            for item, item2 in existing_user:
                user.set_first_name(item.first_name)
                user.set_last_name(item.last_name)
                user.set_age(item.age)
                user.set_gender(item.gender_id)
                user.set_about_me(item.about_me)
                user.set_city({'id': item2.id, 'title': item2.name})

                criteria = self.open_criteria(user_id)
                user.set_criteria(criteria)
                return user

        else:
            return None

    def open_criteria(self, user_id: int) -> Optional[Criteria]:
        """
        Выводит критерии пользователя приложения,
        содержащуюся в экземпляре класса Criteria

       Вводимый параметр:
        - user_id: VK ID пользователя приложения

        Выводимый параметр:
        - Criteria: наполненный экземпляр класса Criteria
        """

        session = self.start_session()
        existing_criteria = session.query(Criteria, Cities). \
            join(Cities, Cities.id == Criteria.city_id). \
            filter(Criteria.user_id == user_id). \
            all()
        session.close()

        if existing_criteria:
            criteria = Criteria()
            for item, item2 in existing_criteria:
                criteria.id = item.id
                criteria.gender_id = 1 if item.gender_id == 2 else 1
                criteria.status = item.status
                criteria.age_from = item.age_from
                criteria.age_to = item.age_to
                criteria.city = {'id': item2.id, 'name': item2.name}
                criteria.has_photo = item.has_photo
                return criteria

        else:
            return Criteria()

    def save_criteria(self, user: User) -> None:
        """
        Сохраняет критерии пользователя

        Вводной параметр:
        - экземпляр класса User
        """

        criteria = user.get_criteria()
        session = self.start_session()
        existing_city = session.query(Cities).\
            filter_by(name=criteria.city['name']).\
            first()

        if not existing_city:
            new_city = Cities(
                id=criteria.city['id'],
                name=criteria.city['name']
            )
            session.add(new_city)
            session.commit()

        criteria_data = session.query(Criteria).\
            filter_by(id=criteria.id, user_id=user.get_user_id()).\
            first()

        if criteria_data:
            criteria_data.gender_id = criteria.gender_id
            criteria_data.status = criteria.status
            criteria_data.age_from = criteria.age_from
            criteria_data.age_to = criteria.age_to
            criteria_data.city_id = criteria.city['id']
            criteria_data.has_photo = criteria.has_photo
            session.commit()

        else:
            all_criteria = session.query(Criteria). \
                all()
            if not all_criteria:
                new_id = 1
            else:
                new_id = len([item for item in all_criteria]) + 1

            new_criteria = Criteria(
                id=new_id,
                user_id=user.get_user_id(),
                gender_id=criteria.gender_id,
                status=criteria.status,
                age_from=criteria.age_from,
                age_to=criteria.age_to,
                city_id=criteria.city['id'],
                has_photo=criteria.has_photo
            )
            session.add(new_criteria)
            session.commit()

        session.close()
