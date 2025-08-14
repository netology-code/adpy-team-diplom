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
    return session.query(User).filter_by(vk_id=vk_id).first()


# ---------------- Кандидаты ----------------
def add_candidate(
    user_id, vk_id, first_name, last_name, city=None, age=None, gender=None
):
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
    return session.query(Favorite).filter_by(user_id=user_id).all()


# ---------------- Чёрный список ----------------
def add_to_blacklist(user_id, vk_candidate_id):
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
    return session.query(Blacklist).filter_by(user_id=user_id).all()
