import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class USERS(Base):
    __tablename__ = 'users'

    id = sq.Column(sq.Integer, primary_key=True)
    id_vk = sq.Column(sq.Integer, unique=True)
    first_name = sq.Column(sq.String(length=40))
    last_name = sq.Column(sq.String(length=40))
    city = sq.Column(sq.String(length=40))
    age = sq.Column(sq.Integer)
    sex = sq.Column(sq.Integer)


    def __str__(self):
        return f" ({self.id}, {self.id_vk}, {self.first_name}, {self.last_name}, {self.city}, {self.age}, {self.sex})"


class PRETENDENTS(Base):
    __tablename__ = 'pretendents'

    id = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.Integer, sq.ForeignKey("users.id"), nullable=False)
    users = relationship(USERS, backref="pretendents")
    id_vk_pret = sq.Column(sq.Integer, unique=True) # по id можно сделать ссылку на профиль
    first_name = sq.Column(sq.String(length=40))
    last_name = sq.Column(sq.String(length=40))
    photo_1 = sq.Column(sq.Text())
    photo_2 = sq.Column(sq.Text())
    photo_3 = sq.Column(sq.Text())

    def __str__(self):
        return f" ({self.id}, {self.id_user}, {self.id_vk}, {self.first_name}, {self.last_name}, {self.photo_1}, {self.photo_2}, {self.photo_3})"


class FAVOURITES(Base):
    __tablename__ = 'favourites'

    id = sq.Column(sq.Integer, primary_key=True)
    id_user = sq.Column(sq.Integer, sq.ForeignKey("users.id"), nullable=False)
    users = relationship(USERS, backref="favourites")
    id_vk_fav = sq.Column(sq.Integer, unique=True) # по id можно сделать ссылку на профиль
    first_name = sq.Column(sq.String(length=40))
    last_name = sq.Column(sq.String(length=40))
    photo_1 = sq.Column(sq.Text())
    photo_2 = sq.Column(sq.Text())
    photo_3 = sq.Column(sq.Text())

    def __str__(self):
        return f" ({self.id}, {self.id_user}, {self.id_vk}, {self.first_name}, {self.last_name}, {self.photo_1}, {self.photo_2}, {self.photo_3})"


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


