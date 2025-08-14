from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    vk_id = Column(Integer, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    city = Column(String)
    age = Column(Integer)
    gender = Column(String)

    candidates = relationship(
        "Candidate", back_populates="owner", cascade="all, delete-orphan"
    )
    favorites = relationship(
        "Favorite", back_populates="user", cascade="all, delete-orphan"
    )
    blacklist = relationship(
        "Blacklist", back_populates="user", cascade="all, delete-orphan"
    )


class Candidate(Base):
    __tablename__ = "candidate"

    id = Column(Integer, primary_key=True)
    vk_id = Column(Integer, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    city = Column(String)
    age = Column(Integer)
    gender = Column(String)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    owner = relationship("User", back_populates="candidates")
    favorite_in = relationship(
        "Favorite", back_populates="candidate", cascade="all, delete-orphan"
    )
    blacklist_in = relationship(
        "Blacklist", back_populates="candidate", cascade="all, delete-orphan"
    )


class Favorite(Base):
    __tablename__ = "favorite"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(
        Integer, ForeignKey("candidate.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    candidate = relationship("Candidate", back_populates="favorite_in")
    user = relationship("User", back_populates="favorites")


class Blacklist(Base):
    __tablename__ = "blacklist"

    id = Column(Integer, primary_key=True)
    candidate_id = Column(
        Integer, ForeignKey("candidate.id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    candidate = relationship("Candidate", back_populates="blacklist_in")
    user = relationship("User", back_populates="blacklist")
