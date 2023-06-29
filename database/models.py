import sqlalchemy as sq
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    user_id = sq.Column(sq.Integer, primary_key=True)
    user_name = sq.Column(sq.String(length=50), unique=True)
    user_gender = sq.Column(sq.String(length=1), nullable=False)
    user_age = sq.Column(sq.Integer, nullable=False)
    user_city = sq.Column(sq.String(length=50), nullable=False)

class Friend(Base):
    __tablename__ = "friend"

    friend_id = sq.Column(sq.Integer, primary_key=True)
    friend_vk_id = sq.Column(sq.Double, nullable=True)
    friend_vk_link = sq.Column(sq.String, nullable=True)

class User_friend(Base):
    __tablename__ = "user_friend"

    user_friend_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("user_id"), nullable=True)
    friend_id = sq.Column(sq.Integer, sq.ForeignKey("friend_id"), nullable=True)
    user_friend = sq.Column(sq.Boolean)

    user = relationship(User, backref="user")
    friend = relationship(User, backref="friend")
