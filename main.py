import os

from sqlalchemy import create_engine
from dotenv import load_dotenv, find_dotenv

from db.create_db import create_tables

if __name__ == '__main__':
    load_dotenv(find_dotenv())
    LOGIN = os.environ.get('LOGIN')
    PSW = os.environ.get('PSW')
    HOST = os.environ.get('HOST')
    PORT = os.environ.get('PORT')
    NAME_BD = os.environ.get('NAME_BD')

    url_database = os.getenv('URL_DATABASE')

    DSN = f'postgresql://postgres:201224@localhost:5432/vkinder'

# URL такого вида postgresql://postgres:postgres@localhost:5432/Vkinder"
# Добавьте в файл .env необходимые конфигурации

    engine = create_engine(DSN)

    create_tables(engine)
