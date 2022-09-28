import psycopg2
from VKUser import VKUser


class DBObject:
    def __init__(self, database, user, password):
        self.database = database
        self.user = user
        self.password = password

    @staticmethod
    def create_user_db(cur):
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
                foto_link VARCHAR(10000) NOT NULL UNIQUE,
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

    @staticmethod
    def add_user(cur, own_id, name, surname, b_date, gender, city, profile_link):
        cur.execute("""
            INSERT INTO user_vk(id, name, surname, b_date, gender, city, profile_link) 
            VALUES(%s, %s, %s, %s, %s, %s, %s);
        """, (own_id, name, surname, b_date, gender, city, profile_link))

    @staticmethod
    def add_possible_pair(cur, own_id, vk_id, name, surname, b_date, gender, city, profile_link):
        cur.execute("""
            INSERT INTO user_vk(id, name, surname, b_date, gender, city, profile_link) 
            VALUES(%s, %s, %s, %s, %s, %s, %s);
        """, (vk_id, name, surname, b_date, gender, city, profile_link))

        cur.execute("""
            INSERT INTO possible_pair(user_id, pair_id) VALUES(%s, %s);
        """, (own_id, vk_id))

    @staticmethod
    def add_user_photos(cur, vk_id, photo_dict: dict):
        # проверить правильность добавления!!
        for link, likes in photo_dict.items():
            cur.execute("""
                INSERT INTO user_photo(user_id, foto_link, likes) VALUES(%s, %s, %s);
            """, (vk_id, link, likes))

    @staticmethod
    def add_user_to_favourites(cur, own_id, vk_id):
        cur.execute("""
            INSERT INTO user_favorite_list(user_id, favourite_id) VALUES(%s, %s);
        """, (own_id, vk_id))

    @staticmethod
    def add_user_to_blacklist(cur, own_id, vk_id):
        cur.execute("""
            INSERT INTO user_black_list(user_id, blocked_id) VALUES(%s, %s);
        """, (own_id, vk_id))

    @staticmethod
    def check_if_in_blacklist(cur, own_id, id):
        cur.execute("""
            SELECT blocked_id FROM user_black_list
            WHERE user_id = %s;
        """, (own_id,))

        blocked_ids = cur.fetchall()

        if len(blocked_ids) > 0:
            ids = [elem[0] for elem in blocked_ids]
            if id in ids:
                return True
        return False

    @staticmethod
    def get_user_photos(cur, id):
        cur.execute("""
            SELECT foto_link, likes FROM user_photo
            WHERE user_id = %s;
        """, (id,))

        photos_likes = cur.fetchall()

        photos_likes_dict = {}

        if len(photos_likes) > 0:
            for photo in photos_likes:
                photos_likes_dict[photo[0]] = photo[1]
        return photos_likes_dict

    @staticmethod
    def select_next_users(cur, own_id, viewed_user_ids=[]):
        tpl_viewed_user_ids = tuple(viewed_user_ids) if len(tuple(viewed_user_ids)) > 0 else ''

        next_ids_db = []

        cur.execute("""
            SELECT pair_id FROM possible_pair
            WHERE user_id = %s;
        """, (own_id,))

        next_ids_db = cur.fetchall()

        if len(next_ids_db) == 0:
            return []
        else:
            next_ids = [elem[0] for elem in next_ids_db]
            return next_ids

    def get_users_info(self, cur):
        next_users = self.select_next_users(cur, own_id, viewed_user_ids=[])
        user_info_list = []

        for id in next_users:
            if id not in viewed_user_ids and not self.check_if_in_blacklist(cur, own_id, id):
                cur.execute("""
                    SELECT * FROM user_vk
                    WHERE id = %s;
                """, (id, ))

                user_infos = cur.fetchall()

                if len(user_infos) > 0:
                    entry = user_infos[0]
                    user_info = VKUser(int(entry[0]), entry[1], entry[2], entry[3], entry[4], entry[5])
                    user_info.url = entry[6]
                    photos_dict = self.get_user_photos(cur, id)
                    user_info.photos_dict = photos_dict
                    user_info_list.append(user_info)

        return user_info_list

# пробная функция выборки пользователей из избранного, уверен ты сделаешь ее лучше
    def show_favorites(self, id):
        cur.execute("""
            SELECT * FROM user_favorite_list
            WHERE favorite_id = %s;
        """, (id,))

        favorites = cur.fetchall()

        return favorites

# Ппробная функция для показа тех кто в черном списке
    def show_all_blaclist(self, id):
        cur.execute("""
            SELECT * FROM user_black_list
            WHERE id = %s;
        """, (id,))

        black_list = cur.fetchall

        return black_list


if __name__ == '__main__':
    db_obj = DBObject('vkinder', 'postgres', 'python123')
    with psycopg2.connect(database=db_obj.database, user=db_obj.user, password=db_obj.password) as conn:
        with conn.cursor() as cur:
            db_obj.create_user_db(cur)
