import psycopg2
import configparser


class VKinderDB:

    def __init__(self, candidate_data):
        self.candidate_data = candidate_data


    def __connect(self):
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

    def __get_id(self, user_id, conn):
        try:
            with conn.cursor() as cur:
                cur.execute(f'''
                SELECT 
                    candidate_id 
                FROM 
                    candidates
                WHERE 
                    user_id = %s;
                ''', (user_id,))
                response = cur.fetchall()[0][0]
            return response
        except:
            conn.close()
            return

    def __add(self):
        conn = self.__connect()
        try:
            with conn.cursor() as cur:
                cur.execute(f'''
                INSERT INTO 
                    candidates(user_id, first_name, last_name, link) 
                VALUES 
                    (%s, %s, %s, %s);
                    ''', (
                    self.candidate_data.get('id'),
                    self.candidate_data.get('first_name'),
                    self.candidate_data.get('last_name'),
                    self.candidate_data.get('link')
                ))
                conn.commit()
                candidate_id = self.__get_id(self.candidate_data.get('id'), conn)
                for el in self.candidate_data.get('photos_ids'):
                    cur.execute(f'''
                    INSERT INTO 
                        photos(photos_ids, candidate_id) 
                    VALUES 
                        (%s, %s);
                        ''', (
                        el,
                        candidate_id
                    ))
                    conn.commit()
                return
        except:
            conn.close()
            return

    def add_favorite(self):
        conn = self.__connect()
        if self.__check(conn, 'black_list'):
            conn.close()
            return 'Невозможно добавить в избранный список, кандидат ' \
                   'находится в черном списке.'
        try:
            self.__add()
            candidate_id = self.__get_id(self.candidate_data.get('id'), conn)
            conn.cursor().execute(f'''
                    INSERT INTO
                        favorite_list(user_id, candidate_id)
                    VALUES
                        (%s, %s);
                        ''', (
                self.candidate_data.get('id'),
                candidate_id
            ))
            conn.commit()
            conn.close()
            return
        except:
            conn.close()
            return

    def add_blask(self):
        conn = self.__connect()
        if self.__check(conn, 'favorite_list'):
            conn.close()
            return 'Невозможно добавить в черный список, кандидат находится ' \
                   'в избранном списке.'
        try:
            self.__add()
            candidate_id = self.__get_id(self.candidate_data.get('id'), conn)
            conn.cursor().execute(f'''
                    INSERT INTO
                        black_list(user_id, candidate_id)
                    VALUES
                        (%s, %s);
                        ''', (
                self.candidate_data.get('id'),
                candidate_id
            ))
            conn.commit()
            conn.close()
            return
        except:
            conn.close()
            return

    def get_all_favorite(self):
        conn = self.__connect()
        try:
            with conn.cursor() as cur:
                cur.execute(f'''
                SELECT 
                    *
                FROM 
                    candidates
                JOIN 
                    favorite_list 
                ON 
                    favorite_list.candidate_id = candidates.candidate_id;
                    ''')
                response_candidates = cur.fetchall()
                cur.execute(f'''
                SELECT
                    *
                FROM
                    photos;
                    ''')
                photos_response = cur.fetchall()
            photos_dict = {}
            if photos_response:
                for el in photos_response:
                    photos_dict[el[2]] = photos_dict.get(el[2], []) + [el[1]]
            candidates_list = []
            if response_candidates:
                for el in response_candidates:
                    information = {
                        'id': el[1], 'first_name': el[2],
                        'last_name': el[3], 'link': el[4],
                        'photos_ids': photos_dict.get(el[0])
                    }
                    candidates_list.append(information)
            else:
                information = []
            conn.close()
            return candidates_list
        except:
            conn.close()
            return

    def get_all_blask(self):
        conn = self.__connect()
        try:
            with conn.cursor() as cur:
                cur.execute(f'''
                        SELECT 
                            *
                        FROM 
                            candidates
                        JOIN 
                            black_list 
                        ON 
                            black_list.candidate_id = candidates.candidate_id;
                            ''')
                response_candidates = cur.fetchall()
                cur.execute(f'''
                        SELECT
                            *
                        FROM
                            photos;
                            ''')
                photos_response = cur.fetchall()
            photos_dict = {}
            if photos_response:
                for el in photos_response:
                    photos_dict[el[2]] = photos_dict.get(el[2], []) + [el[1]]
            candidates_list = []
            if response_candidates:
                for el in response_candidates:
                    information = {
                        'id': el[1], 'first_name': el[2],
                        'last_name': el[3], 'link': el[4],
                        'photos_ids': photos_dict.get(el[0])
                    }
                    candidates_list.append(information)
            else:
                information = []
            conn.close()
            return candidates_list
        except:
            conn.close()
            return

    def delete(self):
        conn = self.__connect()
        try:
            with conn.cursor() as cur:
                cur.execute(f'''
                DELETE FROM 
                    candidates  
                WHERE 
                    candidates.user_id  = {self.candidate_data.get('id')};
                    ''')
                conn.commit()
            conn.close()
        except:
            conn.close()
            return


<<<<<<< HEAD
    def __check(self, conn, table_name):
=======
class Photos(Peoples):

    def __init__(self):
        super().__init__()
        self.table_name = 'photos'
        self.column_name = 'peoples_id'

    def get_photos(self, first_name, last_name):
        id_ = Peoples().get_id(first_name, last_name)
        conn = self.connect()
>>>>>>> ed815dc66577fbcc898a8824bbe4d9b28286e89d
        try:
            with conn.cursor() as cur:
                cur.execute(f'''
                SELECT 
<<<<<<< HEAD
                    user_id
                FROM 
                    {table_name};
                    ''')
                response = cur.fetchall()
            if self.candidate_data.get('id') in [el[0] for el in response]:
                return True
            else:
                return False
        except:
            conn.close()
            return
=======
                    link 
                FROM 
                    {self.table_name}
                JOIN 
                    peoples on 
                    {self.table_name}.{self.column_name} = (
                        SELECT 
                            peoples_id 
                        FROM 
                            peoples 
                        WHERE 
                        peoples_id={id_}
                        )
                ''')
                response = cur.fetchall()
            conn.close()
            return response
        except:
            conn.close()
            return


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
>>>>>>> ed815dc66577fbcc898a8824bbe4d9b28286e89d
