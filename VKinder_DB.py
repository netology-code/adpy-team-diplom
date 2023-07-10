from sqlalchemy.orm import sessionmaker
import sqlalchemy
import json
from VKinder.VKinder_DB import models as m


with open(r'C:\Users\Николаус\PycharmProjects\pythonProject\VKinder\VKinder_DB\config_db.json', 'r') as user_file:
    db_type, login, password, hostname, db_port, db_name = json.load(user_file).values()

DSN = f'{db_type}://{login}:{password}@{hostname}:{db_port}/{db_name}'
engine = sqlalchemy.create_engine(DSN)
m.create_table(engine)

Session = sessionmaker(bind=engine)


def add_user(user_id, first_name, sex, age, city):
    """
        Функция добавляет пользователя в базу данных. В данном случае user - это пользователь, который ищет пару.
    Для простоты будем называть его "пользователь"
    :param user_id: id пользователя
    :param first_name: имя пользователя. Имя нужно лишь для обращения к пользователю при общении с ботом
    :param sex: пол пользователя
    :param age: возраст пользователя
    :param city: город пользователя
    """
    with Session() as session:
        user_find = session.query(m.User.user_id).all()
        if user_id not in [user[0] for user in user_find]:
            user = m.User(user_id=user_id, first_name=first_name, sex=sex, age=age, city=city)
            session.add(user)
        session.commit()


add_user(1, '1', '1', 1, '1')


def add_offer(user_id, offer_id, first_name, last_name, sex, age, city):
    """
    Функция добавляет предложение в базу данных. В данном случае offer - это предложенный пользователю человек из
    поиска. Для простоты будем называть его "предложением" :param vk_user_id: id пользователя :param vk_offer_id: id
    предложения :param first_name: имя предложения :param last_name: фамилия предложения :param sex: пол предложения.
    1 - женский, 2 - мужской :param age: возраст предложения :param city: город предложения
    """
    with Session() as session:
        offer_find = session.query(m.Offer.vk_offer_id).all()
        if offer_id not in [offer[0] for offer in offer_find]:
            offer = m.Offer(vk_offer_id=offer_id, first_name=first_name, last_name=last_name,
                            sex=sex, age=age, city=city)
            session.add(offer)
        user_offer_find = session.query(m.UserOffer.user_offer_id).\
            filter(user_id == m.UserOffer.user_id).\
            filter(m.UserOffer.vk_offer_id == offer_id).all()
        if len(user_offer_find) == 0:
            user_offer = m.UserOffer(user_id=user_id, offer_id=offer_id, black_list=0, favorite_list=0)
            session.add(user_offer)
        session.commit()


def add_black_list(vk_user_id, vk_offer_id):
    """
        Функция добавляет предложение в черный список, если пользователь больше не хочет видеть предложение.
    Предложение скрывается из поиска навсегда
    0 - предложение актуально, 1 - предложение исключено (исключается) из поиска
    :param vk_user_id: id пользователя
    :param vk_offer_id: id предложения
    """
    with Session() as session:
        session.query(m.UserOffer).\
            filter(m.UserOffer.vk_offer_id == vk_offer_id).\
            filter(m.UserOffer.vk_user_id == vk_user_id).\
            filter(m.UserOffer.black_list == 0).\
            update({'black_list': 1})
        session.commit()


def add_favorite(vk_user_id, vk_offer_id):
    """
        Функция добавляет предложение в избранное, если пользователь хочет сохранить предложение.
    0 - предложение неактуально, 1 - предложение включено (включается) в избранное
    :param vk_user_id: id пользователя
    :param vk_offer_id: id предложения
    """
    with Session() as session:
        session.query(m.UserOffer).\
            filter(m.UserOffer.vk_offer_id == vk_offer_id).\
            filter(m.UserOffer.vk_user_id == vk_user_id).\
            filter(m.UserOffer.black_list == 0).\
            update({'favorite_list': 1})
        session.commit()


def add_photo(vk_offer_id, photo_url, count_likes):
    """
        Функция сохраняет в БД ссылки на фотографии предложения
    :param vk_offer_id: id предложения
    :param photo_url: лист со ссылками на фотографии
    :param count_likes: лис с количеством лайков на фотографиях
    """
    with Session() as session:
        for url in photo_url:
            photo = m.Photo(vk_offer_id=vk_offer_id, photo_url=url, count_likes=count_likes)
            session.add(photo)
        session.commit()


def add_interest(interest, vk_user_id=0, vk_offer_id=0):
    """
        Функция добавляет в БД интересы пользователя или предложения
    :param interest: наименование интереса пользователя или предложения
    :param vk_user_id: id пользователя
    :param vk_offer_id: id предложения
    """
    with Session() as session:
        interest_find = session.query(m.Interest.interest).filter(m.Interest.interest == interest)
        if interest not in [interest[0] for interest in interest_find]:
            interest_add = m.Interest(interest="interest")
            session.add(interest_add)
        interest_id_find = session.query(m.Interest.interest_id).filter(m.Interest.interest == interest).all()[0][0]
        user_find = session.query(m.InterestPerson.vk_user_id).\
            filter(m.InterestPerson.interest_id == interest_id_find).\
            filter(m.InterestPerson.vk_user_id == vk_user_id).all()
        offer_find = session.query(m.InterestPerson.vk_offer_id).\
            filter(m.InterestPerson.interest_id == interest_id_find).\
            filter(m.InterestPerson.vk_offer_id == vk_offer_id).all()
        if vk_user_id != 0 and vk_user_id not in [user[0] for user in user_find]:
            interest_person_add = m.InterestPerson(vk_user_id=vk_user_id, interest_id=interest_id_find)
            session.add(interest_person_add)
        if vk_offer_id != 0 and vk_offer_id not in [offer[0] for offer in offer_find]:
            interest_person_add = m.InterestPerson(vk_offer_id=vk_offer_id, interest_id=interest_id_find)
            session.add(interest_person_add)
        session.commit()


def get_offer_info(user_id, offer):
    offer_list = []
    with Session() as session:
        user_interests = session.query(m.Interest.interest). \
            join(m.InterestPerson, m.InterestPerson.interest_id == m.Interest.interest_id). \
            filter(m.InterestPerson.vk_user_id == user_id).all()
        for note in offer:
            offer_list.append([])
            for el in note:
                offer_list[-1].append(el)
            photo = session.query(m.Photo.photo_url).filter(m.Photo.offer_id == note[0]).all()
            offer_list[-1].append([url[0] for url in photo])
            offer_interests = session.query(m.Interest.interest). \
                join(m.InterestPerson, m.InterestPerson.interest_id == m.Interest.interest_id). \
                filter(m.InterestPerson.vk_offer_id == note[0]).all()
            interest_list = []
            for interest in [inter_user[0] for inter_user in user_interests]:
                if interest in [inter_offer[0] for inter_offer in offer_interests]:
                    interest_list.append(interest)
            offer_list[-1].append(interest_list)
    return offer_list


def get_offer(vk_user_id):
    """
        Функция предоставляет сведения о всех предложениях
    :param vk_user_id: id пользователя
    :return: лист, содержащий листы со сведениями о предложениях
            Формат листа:
            [[предложение 1], [предложение 2], ..., [предложение n]]
            Формат предложения:
            [id предложения, 'имя', 'фамилия', пол, возраст, 'город',
            [лист со ссылками на фотографии], [лист с общими интересами пользователя и предложения]]
    """
    with Session() as session:
        offer = session.query(m.Offer.vk_offer_id,
                              m.Offer.first_name,
                              m.Offer.last_name,
                              m.Offer.sex,
                              m.Offer.age,
                              m.Offer.city).\
            join(m.UserOffer, m.UserOffer.vk_offer_id == m.Offer.vk_offer_id).\
            join(m.User, m.User.vk_user_id == m.UserOffer.vk_user_id).\
            filter(m.User.vk_user_id == vk_user_id).\
            filter(m.UserOffer.black_list == 0).all()
        result = get_offer_info(vk_user_id, offer)
    return result


def get_favorite(vk_user_id):
    """
            Функция предоставляет сведения об избранных предложениях
    :param vk_user_id: id пользователя
    :return: лист, содержащий листы со сведениями о предложениях.
            Формат листа:
            [[предложение 1], [предложение 2], ..., [предложение n]]
            Формат предложения:
            [id предложения, 'имя', 'фамилия', пол, возраст, 'город',
            [лист со ссылками на фотографии], [лист с общими интересами пользователя и предложения]]
    """
    with Session() as session:
        offer = session.query(m.Offer.vk_offer_id,
                              m.Offer.first_name,
                              m.Offer.last_name,
                              m.Offer.sex,
                              m.Offer.age,
                              m.Offer.city).\
            join(m.UserOffer, m.UserOffer.vk_offer_id == m.Offer.vk_offer_id).\
            join(m.User, m.User.vk_user_id == m.UserOffer.vk_user_id).\
            filter(m.User.vk_user_id == vk_user_id).\
            filter(m.UserOffer.favorite_list == 1).\
            filter(m.UserOffer.black_list == 0).all()
        result = get_offer_info(vk_user_id, offer)
    return result
