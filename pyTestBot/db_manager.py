import psycopg2
from VKUser import VKUser
from configures import database, user, password
<<<<<<< HEAD
=======

>>>>>>> 4140366ff9c57f7c311954b94769d589a581737e


class DBObject:
    conn = None

    def __init__(self, database, user, password):
        self.database = database
        self.user = user
        self.password = password

    def create_user_db(self, cur):
        cur.execute("""
            DROP TABLE IF EXISTS user_favorite_list;
            DROP TABLE IF EXISTS user_photo;
            DROP TABLE IF EXISTS user_black_list;
            DROP TABLE IF EXISTS possible_pair;
            DROP TABLE IF EXISTS user_vk;
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_vk(
                id INTEGER PRIMARY KEY,
                name VARCHAR(40) NOT NULL,
                surname VARCHAR(40) NOT NULL,
                b_date DATE NOT NULL DEFAULT CURRENT_DATE,
                gender VARCHAR(20) NOT NULL,
                city VARCHAR(20),
                profile_link VARCHAR(60) NOT NULL UNIQUE
            );
         """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_photo(
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES user_vk(id),
                foto_link VARCHAR(10000) NOT NULL,
                likes INTEGER NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS possible_pair(
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES user_vk(id),
                pair_id INTEGER NOT NULL REFERENCES user_vk(id)
            );                
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_favorite_list(
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES user_vk(id),
                favourite_id INTEGER NOT NULL REFERENCES user_vk(id)
            );               
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_black_list(
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES user_vk(id),
                blocked_id INTEGER NOT NULL REFERENCES user_vk(id)
            );
        """)

    def if_user_exists(self, conn, own_id):
        cur = conn.cursor()
        cur.execute("""
                    SELECT * FROM user_vk
                    WHERE id = %s;
                """, (own_id,))

        user_id = cur.fetchall()
        print(f'user id: {user_id}')
        conn.commit()
        return len(user_id)

    def if_pair_exists(self, conn, own_id, pair_id):
        cur = conn.cursor()
        cur.execute("""
                    SELECT id FROM possible_pair
                    WHERE user_id = %s AND pair_id = %s;
                """, (own_id, pair_id))

        pair_id = cur.fetchall()
        print(f'pair id: {pair_id}')
        conn.commit()
        return len(pair_id)

    def add_user(self, conn, own_id, name, surname, b_date, gender, city, profile_link):
        user_check = self.if_user_exists(conn, own_id)
        if user_check == 0:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO user_vk(id, name, surname, b_date, gender, city, profile_link) 
                VALUES(%s, %s, %s, %s, %s, %s, %s);
            """, (own_id, name, surname, b_date, gender, city, profile_link))
            conn.commit()

    def add_possible_pair(self, conn, own_id, vk_id, name, surname, b_date, gender, city, profile_link):
        pair_check = self.if_pair_exists(conn, own_id, vk_id)
        if pair_check == 0:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO user_vk(id, name, surname, b_date, gender, city, profile_link) 
                VALUES(%s, %s, %s, %s, %s, %s, %s);
            """, (vk_id, name, surname, b_date, gender, city, profile_link))
            conn.commit()
            cur_a = conn.cursor()
            cur_a.execute("""
                INSERT INTO possible_pair(user_id, pair_id) VALUES(%s, %s);
            """, (own_id, vk_id))
            conn.commit()

    def add_user_photos(self, conn, vk_id, photo_dict: dict):
        cur = conn.cursor()
        for link, likes in photo_dict.items():
            cur.execute("""
                INSERT INTO user_photo(user_id, foto_link, likes) VALUES(%s, %s, %s);
            """, (vk_id, link, likes))
        conn.commit()

    def add_user_to_favourites(self, conn, own_id, vk_id):
        if not self.check_if_in_favourites(conn, own_id, id):
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO user_favorite_list(user_id, favourite_id) VALUES(%s, %s);
            """, (own_id, vk_id))
            conn.commit()

    def check_if_in_favourites(self, conn, own_id, id):
        cur = conn.cursor()
        cur.execute("""
            SELECT favourite_id FROM user_favorite_list
            WHERE user_id = %s;
        """, (own_id,))

        fav_ids = cur.fetchall()
        conn.commit()

        if len(fav_ids) > 0:
            ids = [elem[0] for elem in fav_ids]
            if id in ids:
                return True
        return False

    def add_user_to_blacklist(self, conn, own_id, vk_id):
        if not self.check_if_in_blacklist(conn, own_id, vk_id):
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO user_black_list(user_id, blocked_id) VALUES(%s, %s);
            """, (own_id, vk_id))
            conn.commit()

    def check_if_in_blacklist(self, conn, own_id, id):
        cur = conn.cursor()
        cur.execute("""
            SELECT blocked_id FROM user_black_list
            WHERE user_id = %s;
        """, (own_id,))

        blocked_ids = cur.fetchall()
        conn.commit()

        if len(blocked_ids) > 0:
            ids = [elem[0] for elem in blocked_ids]
            if id in ids:
                return True
        return False

    def get_user_photos(self, conn, id):
        cur = conn.cursor()
        cur.execute("""
            SELECT foto_link, likes FROM user_photo
            WHERE user_id = %s;
        """, (id,))

        photos_likes = cur.fetchall()
        conn.commit()

        photos_likes_dict = {}

        if len(photos_likes) > 0:
            for photo in photos_likes:
                photos_likes_dict[photo[0]] = photo[1]
        return photos_likes_dict

    def select_next_users(self, conn, own_id):
        cur = conn.cursor()
        cur.execute("""
            SELECT pair_id FROM possible_pair
            WHERE user_id = %s;
        """, (own_id,))

        next_ids_db = cur.fetchall()
        conn.commit()

        if len(next_ids_db) == 0:
            return []
        else:
            next_ids = [elem[0] for elem in next_ids_db]
            return next_ids

    def get_users_info(self, conn, own_id, viewed_user_ids=[]):
        next_users = self.select_next_users(conn, own_id)
        user_info_list = []

        cur = conn.cursor()

        for id in next_users:
            if id not in viewed_user_ids and not self.check_if_in_blacklist(conn, own_id, id):
                cur.execute("""
                    SELECT * FROM user_vk
                    WHERE id = %s;
                """, (id, ))

                user_infos = cur.fetchall()
                conn.commit()

                if len(user_infos) > 0:
                    entry = user_infos[0]
                    user_info = VKUser(int(entry[0]), entry[1], entry[2], entry[3], entry[4], entry[5])
                    user_info.url = entry[6]
                    photos_dict = self.get_user_photos(conn, id)
                    user_info.photos_dict = photos_dict
                    user_info_list.append(user_info)

        return user_info_list

    def show_favorites(self, conn, own_id):
        cur = conn.cursor()
        cur.execute("""
            SELECT favourite_id FROM user_favorite_list
            WHERE user_id = %s;
        """, (own_id,))

        favorites = cur.fetchall()
        conn.commit()

        user_info_list = []
        if len(favorites) > 0:
            ids = [elem[0] for elem in favorites]
            for id in ids:
                cur = conn.cursor()
                cur.execute("""
                SELECT * FROM user_vk
                WHERE id = %s;
                """, (id,))

                user_infos = cur.fetchall()
                conn.commit()

                if len(user_infos) > 0:
                    entry = user_infos[0]
                    user_info = VKUser(int(entry[0]), entry[1], entry[2], entry[3], entry[4], entry[5])
                    user_info.url = entry[6]
                    photos_dict = self.get_user_photos(conn, id)
                    user_info.photos_dict = photos_dict
                    user_info_list.append(user_info)

        return user_info_list

    def show_all_blacklist(self, conn, own_id):
        cur = conn.cursor()
        cur.execute("""
            SELECT blocked_id FROM user_black_list
            WHERE user_id = %s;
        """, (own_id,))

        black_list = cur.fetchall()
        conn.commit()

        user_info_list = []
        if len(black_list) > 0:
            ids = [elem[0] for elem in black_list]
            for id in ids:
                cur = conn.cursor()
                cur.execute("""
                        SELECT * FROM user_vk
                        WHERE id = %s;
                        """, (id,))

                user_infos = cur.fetchall()
                conn.commit()

                if len(user_infos) > 0:
                    entry = user_infos[0]
                    user_info = VKUser(int(entry[0]), entry[1], entry[2], entry[3], entry[4], entry[5])
                    user_info.url = entry[6]
                    photos_dict = self.get_user_photos(conn, id)
                    user_info.photos_dict = photos_dict
                    user_info_list.append(user_info)

        return user_info_list

    def connect(self):
        db_obj = DBObject(database, user, password)
        with psycopg2.connect(database=db_obj.database, user=db_obj.user, password=db_obj.password) as conn:
            with conn.cursor() as cur:
                db_obj.create_user_db(cur)
            self.conn = conn

    def disconnect(self):
        if self.conn:
            self.conn.close()
