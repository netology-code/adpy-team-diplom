from dotenv import load_dotenv
import psycopg2
import os
from CheckBD.ABCCheckDb import ABCCheckDb


class CheckDBSQL(ABCCheckDb):

    def exists_db(self) -> bool:
        """
        Проверка, есть база данных или нет
        Returns:
            bool : True - есть база данных, False - нет базы данных
        """

        connect = psycopg2.connect(dbname='postgres',
                                        user=os.getenv(key='USER_NAME_DB'),
                                        password=os.getenv(key='USER_PASSWORD_DB'))

        with connect.cursor() as cursor:
            cursor = self.connect.cursor()
            cursor.execute("SELECT 1 FROM pg_database WHERE datname='{dbname}'".
                           format(dbname=self.db_name))
            print(cursor.fetchone())
            if cursor.fetchone() is None:
                return False
            else:
                return True

    def create_db(self):
        """
        Создание базы данных
        """
        if not self.exists_db():

            self.connect = psycopg2.connect(dbname='postgres',
                                            user=os.getenv(key='USER_NAME_DB'),
                                            password=os.getenv(key='USER_PASSWORD_DB'))
            self.connect.autocommit = True

            with self.connect.cursor() as cursor:
                cursor = self.connect.cursor()
                try:
                    cursor.execute("CREATE DATABASE %s;" % self.db_name)
                    self.connect.commit()
                except Exception as e:
                    self.error = e
                finally:
                    self.connect.close()

    def exists_tables(self, name_table) -> bool:
        """
        Проверка, все ли нужные таблицы созданы
        Returns:
            bool : True - если созданы, False - нет
        """
        self.connect = psycopg2.connect(dbname=self.db_name,
                                        user=os.getenv(key='USER_NAME_DB'),
                                        password=os.getenv(key='USER_PASSWORD_DB'))

        cur.execute("select exists(select 1 from information_schema.tables where table_name=%s)",
                    [table_name])
        return True if cur.fetchone() else False
        pass

    def create_tables(self):

        self.connect = psycopg2.connect(dbname=self.db_name,
                                        user=os.getenv(key='USER_NAME_DB'),
                                        password=os.getenv(key='USER_PASSWORD_DB'))

        if self.error is None:
            return

        with self.connect.cursor() as cursor:
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS genders(
                        id SERIAL PRIMARY KEY,
                        gender VARCHAR(10)
                    );
                    """)

            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cities(
                        id SERIAL PRIMARY KEY,
                        city VARCHAR(50)
                    );
                    """)

            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users(
                        id SERIAL PRIMARY KEY,
                        first_name VARCHAR(50),
                        last_name VARCHAR(50),
                        age int,
                        gender_id int,
                        city_id int,
                        FOREIGN KEY (gender_id) REFERENCES genders(id),
                        FOREIGN KEY (city_id) REFERENCES cities(id),
                        about_me VARCHAR(200)
                    );
                    """)

            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS favorites(
                                id SERIAL PRIMARY KEY,
                                user_id int,
                                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                                first_name VARCHAR(50),
                                last_name VARCHAR(50),
                                age int,
                                gender_id int,
                                FOREIGN KEY (gender_id) REFERENCES genders(id),
                                profile VARCHAR(50),
                                photo1 VARCHAR(50),
                                photo2 VARCHAR(50),
                                photo3 VARCHAR(50),
                                city_id int,
                                FOREIGN KEY (city_id) REFERENCES cities(id)
                            );
                            """)

            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS exceptions(
                                id SERIAL PRIMARY KEY,
                                user_id int,
                                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                                first_name VARCHAR(50),
                                last_name VARCHAR(50),
                                age int,
                                gender_id int,
                                FOREIGN KEY (gender_id) REFERENCES genders(id),
                                profile VARCHAR(50),
                                photo1 VARCHAR(50),
                                photo2 VARCHAR(50),
                                photo3 VARCHAR(50),
                                city_id int,
                                FOREIGN KEY (city_id) REFERENCES cities(id)
                            );
                            """)
            self.connect.commit()

        # Проверим наличие всех нужных тамблиц
        for name_table in self.tables:
            if not self.exists_tables(name_table):
                self.error = 'Не все таблицы созданы'

    def fill_tables(self):
        pass
