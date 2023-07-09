import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    user_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=60), nullable=False)
    sex = sq.Column(sq.String(length=40), nullable=False)
    age = sq.Column(sq.Integer, nullable=False)
    city = sq.Column(sq.String(length=60), nullable=False)

    user_offer = relationship('UserOffer', back_populates='user')
    interest_person = relationship('InterestPerson', back_populates='user')

    def __str__(self):
        return f'{self.user_id, self.first_name, self.sex, self.age, self.city}'


class Offer(Base):
    __tablename__ = 'offer'

    offer_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=60), nullable=False)
    last_name = sq.Column(sq.String(length=60), nullable=False)
    sex = sq.Column(sq.String(length=40), nullable=False)
    age = sq.Column(sq.Integer, nullable=False)
    city = sq.Column(sq.String(length=60), nullable=False)

    user_offer = relationship('UserOffer', back_populates='offer')
    photo = relationship('Photo', back_populates='offer')
    interest_person = relationship('InterestPerson', back_populates='offer')

    def __str__(self):
        return f'{self.offer_id, self.first_name, self.last_name, self.sex, self.age, self.city}'


class UserOffer(Base):
    __tablename__ = 'user_offer'

    user_offer_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.user_id'), nullable=False)
    offer_id = sq.Column(sq.Integer, sq.ForeignKey('offer.offer_id'), nullable=False)
    favorite_list = sq.Column(sq.Integer, nullable=False, default=0)
    black_list = sq.Column(sq.Integer, nullable=False, default=0)

    user = relationship('User', back_populates='user_offer', cascade='all, delete')
    offer = relationship('Offer', back_populates='user_offer', cascade='all, delete')

    def __str__(self):
        return f'{self.black_list}'


class Interest(Base):
    __tablename__ = 'interest'

    interest_id = sq.Column(sq.Integer, primary_key=True)
    interest = sq.Column(sq.String(length=60), nullable=False)

    interest_person = relationship('InterestPerson', back_populates='interest')

    def __str__(self):
        return self.interest


class InterestPerson(Base):
    __tablename__ = 'interest_person'

    interest_person_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.user_id'), nullable=False)
    offer_id = sq.Column(sq.Integer, sq.ForeignKey('offer.offer_id'), nullable=False)
    interest_id = sq.Column(sq.Integer, sq.ForeignKey('interest.interest_id'), nullable=False)

    user = relationship('User', back_populates='interest_person', cascade='all, delete')
    offer = relationship('Offer', back_populates='interest_person', cascade='all, delete')
    interest = relationship('Interest', back_populates='interest_person', cascade='all, delete')


class Photo(Base):
    __tablename__ = 'photo'

    photo_id = sq.Column(sq.Integer, primary_key=True)
    offer_id = sq.Column(sq.Integer, sq.ForeignKey('offer.offer_id'), nullable=False)
    photo_url = sq.Column(sq.String(length=100), nullable=False)
    count_likes = sq.Column(sq.Integer, nullable=False)

    photo = relationship('Offer', back_populates='photo', cascade='all, delete')

    def __str__(self):
        return f'{self.offer_id, self.photo_url}'


def create_table(engine):
    Base.metadata.create_all(engine)


def delete_table(engine):
    Base.metadata.delete_all(engine)
