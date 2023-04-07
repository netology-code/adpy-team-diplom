import psycopg2
import configparser


class Peoples:

    def __init__(self):
        self.table_name = 'peoples'
        self.column_name = 'peoples_id'

    @staticmethod
    def connect():
        try:
            config = configparser.ConfigParser()
            config.read("settings.ini")
            user = config["settings"]["user"]
            password = config["settings"]["password"]
            name_db = 'vkinder_db'
            conn = psycopg2.connect(database=name_db, user=user,
                                    password=password)
            return conn
        except:
            return

    def insert(self, dict_: dict):
        conn = self.connect()
        try:
            column_name = [el for el in dict_.keys()]
            value = [el for el in dict_.values()]
            s = ', '.join(['%s'] * len(dict_))
            conn.cursor().execute(f'''
            INSERT INTO 
                {self.table_name}({', '.join(column_name)}) 
            VALUES 
                ({s});
                ''', (value))
            conn.commit()
            conn.close()
            return
        except:
            conn.close()
            return

    def select(self, table_name: str):
        conn = self.connect()
        try:
            with conn.cursor() as cur:
                cur.execute(f'''
                SELECT
                    peoples.peoples_id, id_vk, first_name, last_name, city, sex
                FROM
                    peoples
                JOIN
                    {table_name} on peoples.peoples_id = {table_name}.peoples_id;
                ''')
                response = cur.fetchall()
            conn.close()
            return response
        except:
            conn.close()
            return

    def get_all(self):
        conn = self.connect()
        try:
            with conn.cursor() as cur:
                cur.execute(f'''
                SELECT 
                    * 
                FROM 
                    {self.table_name};
                ''')
                response = cur.fetchall()
            conn.close()
            return response
        except:
            conn.close()
            return

    def search_name(self, first_name: str, last_name: str):
        conn = self.connect()
        try:
            with conn.cursor() as cur:
                cur.execute(f'''
                SELECT 
                    * 
                FROM 
                    {self.table_name}
                WHERE 
                    first_name = %s
                    and
                    last_name = %s;
                ''', (first_name, last_name))
                response = cur.fetchall()
            conn.close()
            return response
        except:
            conn.close()
            return

    def search_age(self, start=0, stop=100):
        conn = self.connect()
        try:
            with conn.cursor() as cur:
                cur.execute(f'''
                SELECT 
                    * 
                FROM 
                    {self.table_name}
                WHERE 
                    age between %s and %s;
                ''', (start, stop))
                response = cur.fetchall()
            conn.close()
            return response
        except:
            conn.close()
            return

    def search_city(self, city: str):
        conn = self.connect()
        try:
            with conn.cursor() as cur:
                cur.execute(f'''
                SELECT 
                    * 
                FROM 
                    {self.table_name}
                WHERE 
                    city = %s;
                ''', (city,))
                response = cur.fetchall()
            conn.close()
            return response
        except:
            conn.close()
            return

    def search_sex(self, sex: int):
        conn = self.connect()
        try:
            with conn.cursor() as cur:
                cur.execute(f'''
                SELECT 
                    * 
                FROM 
                    {self.table_name}
                WHERE 
                    sex = %s;
                ''', (sex,))
                response = cur.fetchall()
            conn.close()
            return response
        except:
            conn.close()
            return

    def search_all_parameters(
            self, first_name: str, last_name: str, city: str, sex: int,
            min_age=0, max_age=100
    ):
        conn = self.connect()
        try:
            with conn.cursor() as cur:
                cur.execute(f'''
                SELECT 
                    * 
                FROM 
                    {self.table_name}
                WHERE
                    first_name = %s
                    and
                    last_name = %s
                    and
                    age between %s and %s
                    and
                    city = %s
                    and
                    sex = %s;
                ''', (first_name, last_name, min_age, max_age, city, sex))
                response = cur.fetchall()
            conn.close()
            return response
        except:
            conn.close()
            return

    def check(self, peoples_id: int, table_name: str):
        check_list = [el[0] for el in self.select(table_name)]
        if peoples_id in check_list:
            return False
        else:
            return True

    def get_id(self, first_name: str, last_name: str):
        people_id = self.search_name(first_name, last_name)
        return people_id[0][0]

    def delete(self, people_id):
        conn = self.connect()
        try:
            with conn.cursor() as cur:
                cur.execute(f'''
                DELETE FROM 
                    {self.table_name} 
                WHERE 
                    {self.column_name} = %s;
                ''', (people_id,))
                conn.commit()
            conn.close()
            return
        except:
            conn.close()
            return


class Photos(Peoples):

    def __init__(self):
        super().__init__()
        self.table_name = 'photos'
        self.column_name = 'peoples_id'


class Favorite(Peoples):

    def __init__(self):
        super().__init__()
        self.table_name = 'favorite_people'
        self.column_name = 'peoples_id'

    def insert(self, id_):
        if self.check(id_, 'black_list'):
            conn = self.connect()
            try:
                with conn.cursor() as cur:
                    cur.execute(f'''
                    INSERT INTO 
                        {self.table_name}({self.column_name}) 
                    VALUES 
                        (%s);
                    ''', (id_,))
                    conn.commit()
                conn.close()
                return
            except:
                conn.close()
                return
        else:
            return 'Невозможно добавить в избранное, человек находится в ' \
                   'чёрном списке.'


class BlackList(Peoples):

    def __init__(self):
        super().__init__()
        self.table_name = 'black_list'
        self.column_name = 'peoples_id'

    def insert(self, id_):
        if self.check(id_, 'favorite_people'):
            conn = self.connect()
            try:
                with conn.cursor() as cur:
                    cur.execute(f'''
                                INSERT INTO 
                                    {self.table_name}({self.column_name}) 
                                VALUES 
                                    (%s);
                                ''', (id_,))
                    conn.commit()
                conn.close()
                return
            except:
                conn.close()
                return
        else:
            return 'Невозможно добавить в чёрный список, человек находится в ' \
                   'избранном.'
