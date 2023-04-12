import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import configparser
from time import sleep


class CreateDatabase:

    def __init__(self, db_name, user, password):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.data_checking = True

    def connection_psql(self):
        connection = psycopg2.connect(user=self.user, password=self.password)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return connection

    def connection_db(self):
        connection = psycopg2.connect(
            database=self.db_name, user=self.user, password=self.password
        )
        cursor = connection.cursor()
        return connection, cursor

    def checking_database(self):
        try:
            connection, cursor = self.connection_db()
            cursor.close()
            connection.close()
            return print(
                f'Подключение к базе данных {self.db_name} прошло успешно.'
            )
        except (Exception, Error):
            self.create_db()

    def create_db(self):
        try:
            connection = self.connection_psql()
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE {self.db_name}")
            connection.commit()
            cursor.close()
            connection.close()
            print('База данных создана успешно.')
            self.create_table()
            return
        except (Exception, Error):
            self.data_checking = False
            return self.data_checking

    def create_table(self):
<<<<<<< HEAD
        with psycopg2.connect(database=self.db_name, user=self.user,
                              password=self.password) as conn:
            with conn.cursor() as cur:
                cur.execute('''
                CREATE TABLE IF NOT EXISTS candidates(
                    candidate_id SERIAL PRIMARY KEY,
                    user_id BIGINT UNIQUE NOT NULL,
                    first_name VARCHAR(40),
                    last_name VARCHAR(40),
                    link VARCHAR(100) UNIQUE
                );
                ''')

                cur.execute('''
                CREATE TABLE IF NOT EXISTS photos(
                    photos_id SERIAL PRIMARY KEY,
                    photos_ids BIGINT UNIQUE,
                    candidate_id INTEGER NOT NULL 
                        REFERENCES candidates(candidate_id) ON DELETE CASCADE
                );
                ''')

                cur.execute('''
                CREATE TABLE IF NOT EXISTS favorite_list(
                    favorite_list_id SERIAL PRIMARY KEY,
                    user_id BIGINT UNIQUE,
                    candidate_id INTEGER NOT NULL 
                        REFERENCES candidates(candidate_id) ON DELETE CASCADE
                );
                ''')

                cur.execute('''
                CREATE TABLE IF NOT EXISTS black_list(
                    black_list_id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE,
                    candidate_id INTEGER NOT NULL 
                        REFERENCES candidates(candidate_id) ON DELETE CASCADE
                );
                ''')
        conn.close()
=======
        connection, cursor = self.connection_db()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS peoples(
            peoples_id SERIAL PRIMARY KEY,
            id_vk INTEGER UNIQUE,
            first_name VARCHAR(40),
            last_name VARCHAR(40),
            age INTEGER,
            city VARCHAR(40),
            sex INTEGER CHECK (sex >= 0) CHECK (sex <= 2)
        );
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos(
            photos_id SERIAL PRIMARY KEY,
            link VARCHAR(250) UNIQUE,
            peoples_id INTEGER NOT NULL 
                REFERENCES peoples(peoples_id) ON DELETE CASCADE
        );
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorite_people(
            favorite_people_id SERIAL PRIMARY KEY,
            peoples_id INTEGER UNIQUE NOT NULL 
                REFERENCES peoples(peoples_id) ON DELETE CASCADE
        );
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS black_list(
            black_list_id SERIAL PRIMARY KEY,
            peoples_id INTEGER UNIQUE NOT NULL 
                REFERENCES peoples(peoples_id) ON DELETE CASCADE
        );
        ''')
        connection.commit()
        cursor.close()
        connection.close()
>>>>>>> ed815dc66577fbcc898a8824bbe4d9b28286e89d
        print(f'Таблицы созданы успешно.')
        return


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("settings.ini")
    user_ = config["settings"]["user"]
    password_ = config["settings"]["password"]
    name_db = 'vkinder_db'
    db = CreateDatabase(name_db, user_, password_)
    db.checking_database()
    if not (db.__dict__.get('data_checking')):
        print('Проверьте данные в файле settings и повторите попытку.')
    sleep(3)
