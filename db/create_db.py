from sqlalchemy import Integer, String, ForeignKey, Column
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    user_id: int = Column(Integer, primary_key=True, index=True)
    vk_id: int = Column(Integer, nullable=False, index=True)
    age: int = Column(Integer)
    city: str = Column(String)
    gender: int = Column(Integer)
    state: int = Column(Integer)
    offset: int = Column(Integer)
    last_id: int = Column(Integer, index=True)


class Partner(Base):
    __tablename__ = 'partners'
    partner_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    partner_vk_id = Column(Integer, nullable=False)
    name = Column(String(20))
    surname = Column(String(40))
    gender = Column(Integer)
    age = Column(Integer)
    foto = Column(MutableList.as_mutable(ARRAY(String(100))))
    link = Column(String)

    users_partner = relationship('Users', backref='user_id_part')


class Favorite(Base):
    __tablename__ = 'favorites'
    favorite_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    partner_id = Column(Integer, ForeignKey('partners.partner_id'), nullable=False, index=True)

    users_favorite = relationship('Users', backref='user_id_favor')
    partner_favor = relationship('Partner', backref='partner_id_acc')


class Blacklist(Base):
    __tablename__ = 'blacklist'
    blacklist_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    partner_id = Column(Integer, ForeignKey('partners.partner_id'), nullable=False, index=True)

    users_blacklist = relationship('Users', backref='user_id_black')
    partner_blacklist = relationship('Partner', backref='partner_id_black')


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)