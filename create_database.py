import psycopg2
import configparser
from time import sleep


class CreateDatabase:

    def __init__(self, db_name, user, password):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.data_checking = True

    def checking_database(self):
        try:
            conn = psycopg2.connect(database=self.db_name, user=self.user,
                                    password=self.password)
            conn.close()
            return print(
                f'Подключение к базе данных {self.db_name} прошло успешно.'
            )
        except:
            self.create_db()

    def create_db(self):
        try:
            conn = psycopg2.connect(user=self.user, password=self.password)
            with conn.cursor() as cur:
                conn.autocommit = True
                cur.execute(f"CREATE DATABASE {self.db_name}")
            conn.close()
            print('База данных создана успешно.')
            self.create_table()
            return
        except:
            self.data_checking = False
            return self.data_checking

    def create_table(self):
        with psycopg2.connect(database=f'{self.db_name}', user=self.user,
                              password=self.password) as conn:
            with conn.cursor() as cur:
                cur.execute('''
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

                cur.execute('''
                CREATE TABLE IF NOT EXISTS photos(
                    photos_id SERIAL PRIMARY KEY,
                    link VARCHAR(250) UNIQUE,
                    peoples_id INTEGER NOT NULL 
                        REFERENCES peoples(peoples_id) ON DELETE CASCADE
                );
                ''')
                conn.commit()

                cur.execute('''
                CREATE TABLE IF NOT EXISTS favorite_people(
                    favorite_people_id SERIAL PRIMARY KEY,
                    peoples_id INTEGER UNIQUE NOT NULL 
                        REFERENCES peoples(peoples_id) ON DELETE CASCADE
                );
                ''')
                conn.commit()

                cur.execute('''
                CREATE TABLE IF NOT EXISTS black_list(
                    black_list_id SERIAL PRIMARY KEY,
                    peoples_id INTEGER UNIQUE NOT NULL 
                        REFERENCES peoples(peoples_id) ON DELETE CASCADE
                );
                ''')
                conn.commit()

        print(f'Таблицы созданы успешно.')
        return


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("settings.ini")
    user = config["settings"]["user"]
    password = config["settings"]["password"]
    name_db = 'vkinder_db'
    db = CreateDatabase(name_db, user, password)
    db.checking_database()
    if not (db.__dict__.get('data_checking')):
        print('Проверьте данные в файле settings и повторите попытку.')
    sleep(3)
