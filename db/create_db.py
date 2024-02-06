from sqlalchemy import Integer, String, ForeignKey, Column
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, index=True)
    vk_id = Column(Integer, nullable=False, index=True)


class Applicant(Base):
    __tablename__ = 'applicants'
    applicant_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    applicant_vk_id = Column(Integer, nullable=False)
    name = Column(String(20))
    surname = Column(String(40))
    gender = Column(String(10))
    age = Column(Integer)
    foto = Column(String)
    link = Column(String)
    users = relationship('User', backref='user_id')


class Favorite(Base):
    __tablename__ = 'favorites'
    favorite_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    applicant_id = Column(Integer, ForeignKey('applicants.applicant_id'), nullable=False)

    users = relationship('User', backref='user_id')
    applicant = relationship('Applicant', backref='applicant_id')


class Blacklist(Base):
    __tablename__ = 'blacklist'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    applicant_id = Column(Integer, ForeignKey('applicants.applicant_id'), nullable=False)
    users = relationship('User', backref='user_id')
    applicant = relationship('Applicant', backref='applicant_id')


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
