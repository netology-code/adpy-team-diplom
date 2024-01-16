import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import create_tables


DSN = 'postgresql://postgres:touching@localhost:5432/VKinder'
engine = sqlalchemy.create_engine(DSN)

create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()

session.close()