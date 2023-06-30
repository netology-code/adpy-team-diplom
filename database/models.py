import sqlalchemy as sq
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "user"

    user_id = sq.Column(sq.Bigint, primary_key=True)
    user_name = sq.Column(sq.String(length=50), unique=True)
    search_gender = sq.Column(sq.String(length=1), nullable=False)
    search_age = sq.Column(sq.Integer, nullable=False)
    search_city = sq.Column(sq.String(length=50), nullable=False)

class Favorite(Base):
    __tablename__ = "favorite"

    user_id = sq.Column(sq.Bigint, sq.ForeignKey("user_id"), nullable=True)
    favorite_vk_user_id = sq.Column(sq.Bigint, nullable=True)

    favorite = relationship(User, backref="user")

class Blacklist(Base):
    __tablename__ = "blacklist"

    user_id = sq.Column(sq.Bigint, sq.ForeignKey("user_id"), nullable=True)
    blocked_vk_user_id = sq.Column(sq.Integer)

    user = relationship(User, backref="user")
    
class State(Base):
    __tablename__ = "state"

    user_id = sq.Column(sq.Bigint, sq.ForeignKey("user_id"), nullable=True)
    state = sq.Column(sq.Integer)

    user = relationship(User, backref="user")
