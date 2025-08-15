import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Candidate, Favorite, Blacklist

# Загружаем .env
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Создаём движок
engine = create_engine(DATABASE_URL)

# Создаём сессию
Session = sessionmaker(bind=engine)
session = Session()

# Создаём таблицы, если их нет
Base.metadata.create_all(engine)


# ---------------- CRUD функции ---------------- #


# ---------------- Пользователи ----------------
def create_user(vk_id, first_name, last_name, city=None, age=None, gender=None):
    """Создаёт нового пользователя в БД, если он ещё не существует.

    Args:
        vk_id (int): ID пользователя ВКонтакте.
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        city (str, optional): Город пользователя.
        age (int, optional): Возраст пользователя.
        gender (str, optional): Пол пользователя.

    Returns:
        User: Объект пользователя.
    """
    user = session.query(User).filter_by(vk_id=vk_id).first()
    if not user:
        user = User(
            vk_id=vk_id,
            first_name=first_name,
            last_name=last_name,
            city=city,
            age=age,
            gender=gender,
        )
        session.add(user)
        session.commit()
    return user


def get_user(vk_id):
    """Возвращает пользователя из БД по его VK ID.

    Args:
        vk_id (int): ID пользователя ВКонтакте.

    Returns:
        User | None: Объект пользователя или None, если не найден.
    """
    return session.query(User).filter_by(vk_id=vk_id).first()


# ---------------- Кандидаты ----------------
def add_candidate(
    user_id, vk_id, first_name, last_name, city=None, age=None, gender=None
):
    """Добавляет кандидата в БД для конкретного пользователя.

    Args:
        user_id (int): ID пользователя в таблице users.
        vk_id (int): ID кандидата ВКонтакте.
        first_name (str): Имя кандидата.
        last_name (str): Фамилия кандидата.
        city (str, optional): Город кандидата.
        age (int, optional): Возраст кандидата.
        gender (str, optional): Пол кандидата.

    Returns:
        Candidate: Объект кандидата.
    """
    candidate = session.query(Candidate).filter_by(vk_id=vk_id, user_id=user_id).first()
    if not candidate:
        candidate = Candidate(
            vk_id=vk_id,
            first_name=first_name,
            last_name=last_name,
            city=city,
            age=age,
            gender=gender,
            user_id=user_id,
        )
        session.add(candidate)
        session.commit()
    return candidate


# ---------------- Избранное ----------------
def add_to_favorites(user_id, vk_candidate_id):
    """Добавляет кандидата в избранное для пользователя.

    Args:
        user_id (int): ID пользователя в таблице users.
        vk_candidate_id (int): ID кандидата ВКонтакте.

    Returns:
        Favorite: Объект избранного.
    """
    candidate = (
        session.query(Candidate)
        .filter_by(vk_id=vk_candidate_id, user_id=user_id)
        .first()
    )
    if not candidate:
        candidate = add_candidate(user_id, vk_candidate_id, "Неизвестно", "")
    fav = (
        session.query(Favorite)
        .filter_by(user_id=user_id, candidate_id=candidate.id)
        .first()
    )
    if not fav:
        fav = Favorite(user_id=user_id, candidate_id=candidate.id)
        session.add(fav)
        session.commit()
    return fav


def get_favorites(user_id):
    """Возвращает список избранных кандидатов пользователя.

    Args:
        user_id (int): ID пользователя в таблице users.

    Returns:
        list[Favorite]: Список объектов избранного.
    """
    return session.query(Favorite).filter_by(user_id=user_id).all()


# ---------------- Чёрный список ----------------
def add_to_blacklist(user_id, vk_candidate_id):
    """Добавляет кандидата в чёрный список пользователя.

    Args:
        user_id (int): ID пользователя в таблице users.
        vk_candidate_id (int): ID кандидата ВКонтакте.

    Returns:
        Blacklist: Объект чёрного списка.
    """
    candidate = (
        session.query(Candidate)
        .filter_by(vk_id=vk_candidate_id, user_id=user_id)
        .first()
    )
    if not candidate:
        candidate = add_candidate(user_id, vk_candidate_id, "Неизвестно", "")
    bl = (
        session.query(Blacklist)
        .filter_by(user_id=user_id, candidate_id=candidate.id)
        .first()
    )
    if not bl:
        bl = Blacklist(candidate_id=candidate.id, user_id=user_id)
        session.add(bl)
        session.commit()
    return bl


def get_blacklist(user_id):
    """Возвращает список кандидатов из чёрного списка пользователя.

    Args:
        user_id (int): ID пользователя в таблице users.

    Returns:
        list[Blacklist]: Список объектов чёрного списка.
    """
    return session.query(Blacklist).filter_by(user_id=user_id).all()
