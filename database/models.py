import sqlalchemy as sq
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    user_id = sq.Column(sq.BigInteger, primary_key=True)
    user_name = sq.Column(sq.String(length=50), unique=True)
    search_gender = sq.Column(sq.String(length=1), nullable=False)
    search_age = sq.Column(sq.Integer, nullable=False)
    search_city = sq.Column(sq.String(length=50), nullable=False)

class Favorite(Base):
    __tablename__ = "favorite"

    favorite_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.BigInteger, sq.ForeignKey("user_id"), nullable=False)
    favorite_vk_user_id = sq.Column(sq.BigInteger, nullable=True)

    favorite = relationship(User, backref="user")

class Blacklist(Base):
    __tablename__ = "blacklist"

    blacklist_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.BigInteger, sq.ForeignKey("user_id"), nullable=False)
    blocked_vk_user_id = sq.Column(sq.Integer, nullable=True)

    user = relationship(User, backref="user")
    
class State(Base):
    __tablename__ = "state"

    state_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.BigInteger, sq.ForeignKey("user_id"), nullable=False)
    state = sq.Column(sq.Integer)

    user = relationship(User, backref="user")
