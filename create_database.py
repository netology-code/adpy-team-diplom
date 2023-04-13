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
                    user_id INTEGER UNIQUE,
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
