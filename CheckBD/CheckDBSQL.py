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

        self.connect = psycopg2.connect(dbname='postgres',
                                        user=os.getenv(key='USER_NAME_DB'),
                                        password=os.getenv(key='USER_PASSWORD_DB'))

        with self.connect.cursor() as cursor:
            cursor = self.connect.cursor()
            cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s", (self.db_name,))


            if cursor.fetchone() is None:
                return False
            else:
                self.connect.close()
                self.connect = psycopg2.connect(dbname=self.db_name,
                                                user=os.getenv(key='USER_NAME_DB'),
                                                password=os.getenv(key='USER_PASSWORD_DB'))
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
                    print(e)
                finally:
                    self.connect.close()
                    self.connect = psycopg2.connect(dbname=self.db_name,
                                                    user=os.getenv(key='USER_NAME_DB'),
                                                    password=os.getenv(key='USER_PASSWORD_DB'))

    def exists_tables(self, table_name) -> bool:
        """
        Проверка, все ли нужные таблицы созданы
        :param table_name: имя таблицы для проверки
        Returns:
            bool : True - если созданы, False - нет
        """
        with self.connect.cursor() as cursor:
            cursor.execute("select exists(select 1 from information_schema.tables where table_name=%s)",
                        [table_name])
            return True if cursor.fetchone() else False

    def create_tables(self):

        if not self.error is None:
            return

        with self.connect.cursor() as cursor:

            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS genders(
                        id SERIAL PRIMARY KEY,
                        gender VARCHAR(10) NOT NULL
                    );
                    """)

            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cities(
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(50) NOT NULL
                    );
                    """)

            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users(
                        id SERIAL PRIMARY KEY,
                        first_name VARCHAR(50) NOT NULL,
                        last_name VARCHAR(50) NOT NULL,
                        age int NOT NULL,
                        gender_id int NOT NULL,
                        city_id int NOT NULL,
                        FOREIGN KEY (gender_id) REFERENCES genders(id),
                        FOREIGN KEY (city_id) REFERENCES cities(id),
                        about_me VARCHAR(1500)
                    );
                    """)

            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS criteria(
                            id SERIAL PRIMARY KEY,
                            user_id int NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                            gender_id int NOT NULL,
                            status int NOT NULL,
                            age_from int NOT NULL,
                            age_to int NOT NULL,
                            city_id int NOT NULL,
                            has_photo int NOT NULL
                        );
                        """)

            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS favorites(
                                id SERIAL PRIMARY KEY,
                                user_id int NOT NULL,
                                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                                first_name VARCHAR(50) NOT NULL,
                                last_name VARCHAR(50) NOT NULL,
                                age int NOT NULL,
                                gender_id int NOT NULL,
                                FOREIGN KEY (gender_id) REFERENCES genders(id),
                                profile VARCHAR(50) NOT NULL,
                                photo1 VARCHAR(1000),
                                photo2 VARCHAR(1000),
                                photo3 VARCHAR(1000),
                                city_id int NOT NULL,
                                FOREIGN KEY (city_id) REFERENCES cities(id)
                            );
                            """)

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS exceptions(
                                id SERIAL PRIMARY KEY,
                                user_id int NOT NULL,
                                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                                first_name VARCHAR(50) NOT NULL,
                                last_name VARCHAR(50) NOT NULL,
                                age int NOT NULL,
                                gender_id int NOT NULL,
                                FOREIGN KEY (gender_id) REFERENCES genders(id),
                                profile VARCHAR(50) NOT NULL,
                                photo1 VARCHAR(1000),
                                photo2 VARCHAR(1000),
                                photo3 VARCHAR(1000),
                                city_id int NOT NULL,
                                FOREIGN KEY (city_id) REFERENCES cities(id)
                            );
                            """)
            self.connect.commit()

        # Проверим наличие всех нужных тамблиц
        for name_table in self.tables:
            if not self.exists_tables(name_table):
                self.error = 'Не все таблицы созданы'

    def fill_tables(self):
        """
        Заполнение предопределенных данных
        :return:
        """

        if not self.error is None:
            return

        sql = """SELECT * FROM genders;"""
        with self.connect.cursor() as cursor:
            cursor.execute(sql)
            if len(cursor.fetchall()) == 0:
                sql = """INSERT INTO genders(id, gender)
                             VALUES(%s, %s);"""
                cursor.execute(sql, (1, 'Женщина'))
                cursor.execute(sql, (2, 'Мужчина'))
                self.connect.commit()

        self.connect.close()
