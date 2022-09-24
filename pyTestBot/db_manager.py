import psycopg2
#pip install psycopg2

class VKUser:
    url = ''
    photos_dict = {}
    relation = ''
    favourites_list = []

    def __init__(self, id, name, surname, bdate, gender, city):
        self.id = id
        self.name = name
        self.surname = surname
        self.bdate = bdate
        self.gender = gender
        self.city = city

class DBObject:
    def __init__(self, database, user, password):
        self.database = database
        self.user = user
        self.password = password

    def create_user_db(self):
        with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                 DROP TABLE public.userfavouritlist;
                 DROP TABLE public.userfoto;
                 DROP TABLE public.userblacklist;
                 DROP TABLE public.possiblepair;
                 DROP TABLE public.user;
                 """)

                cur.execute("""
                 CREATE TABLE IF NOT EXISTS public.User(
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
                CREATE TABLE IF NOT EXISTS public.UserFoto(
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES public.User(id),
                foto_link VARCHAR(200) NOT NULL UNIQUE,
                likes INTEGER NOT NULL
                );
                """)

                cur.execute("""
                CREATE TABLE IF NOT EXISTS public.PossiblePair(
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES public.User(id),
                pair_id INTEGER NOT NULL REFERENCES public.User(id)
                );                
                """)

                cur.execute("""
                CREATE TABLE IF NOT EXISTS public.UserFavouritList(
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES public.User(id),
                favourite_id INTEGER NOT NULL REFERENCES public.User(id)
                );               
                """)

                cur.execute("""
                CREATE TABLE IF NOT EXISTS public.UserBlackList(
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES public.User(id),
                blocked_id INTEGER NOT NULL REFERENCES public.User(id)
                );
                """)

                conn.commit()
        conn.close()

    def add_possible_pair(self, own_id, vk_id, name, surname, b_date, gender, city, profile_link):
        with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO public.User(id, name, surname, b_date, gender, city, profile_link) VALUES(%s, %s, %s);
                """, (vk_id, name, surname, b_date, gender, city, profile_link))
                conn.commit()

            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO public.PossiblePair(user_id, pair_id) VALUES(%s, %s, %s);
                """, (own_id, vk_id))
                conn.commit()

        conn.close()

    def add_user_photos(self, vk_id, photo_dict:dict):
        with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
            with conn.cursor() as cur:
                #проверить правильность добавления!!
                for link, likes in photo_dict.items():
                    cur.execute("""
                    INSERT INTO public.UserFoto(user_id, foto_link, likes) VALUES(%s, %s, %s);
                    """, (vk_id, link, likes))
            conn.commit()
        conn.close()

    def add_user_to_favourites(self, own_id, vk_id):
        with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO public.UserFavouritList(user_id, favourite_id) VALUES(%s, %s, %s);
                """, (own_id, vk_id))
            conn.commit()
        conn.close()

    def add_user_to_blacklist(self, own_id, vk_id):
        with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO public.UserBlackList(user_id, blocked_id) VALUES(%s, %s, %s);
                """, (own_id, vk_id))
            conn.commit()
        conn.close()

    def check_if_in_blacklist(self, own_id, id):
        with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                        SELECT blocked_id FROM public.UserBlacklist
                        WHERE user_id = %s;
                        """, (own_id,))
                blocked_ids = cur.fetchall()
            conn.commit()
        conn.close()

        if len(blocked_ids) > 0:
            ids = [elem[0] for elem in blocked_ids]
            if id in ids:
                return True
        return False

    def get_user_photos(self, id):
        with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                        SELECT foto_link, likes FROM public.UserFoto
                        WHERE user_id = %s;
                        """, (id,))
                photos_likes = cur.fetchall()
            conn.commit()
        conn.close()

        photos_likes_dict = {}
        if len(photos_likes) > 0:
            for photo in photos_likes:
                photos_likes_dict[photo[0]] = photo[1]
        return photos_likes_dict


    #viewed_user_ids лист с id уже просмотренных пользователей. Первый пользователь показывается автоматически и его id надо занести в список, как просмотренный
    #если БД не дает больше результатов поиска, после нажатия кнопки next и обращения к БД, то надо снова сделать users.search
    def select_next_user(self, own_id, viewed_user_ids = []):
        with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
            with conn.cursor() as cur:
                 cur.execute("""
                 SELECT pair_id FROM public.PossiblePair
                 WHERE user_id = %s;
                 """, (own_id,))
                 next_ids_db = cur.fetchall()
            conn.commit()
        conn.close()

        if not next_ids_db:
            #если при вызове функции нет информации в БД, то необходима загрузка новых пользователей
            return 1
        else:
            next_ids = [elem[0] for elem in next_ids_db]
            print(next_ids)

        user_info_list = []

        #проход в цикле по каждому id возможной пары
        for id in next_ids:
            #если id не находится в уже просмотренных и не в черном списке, то загрузи информацию о пользователе и его фото из БД
            if id not in viewed_user_ids and not self.check_if_in_blacklist(own_id, id):
                with psycopg2.connect(database=self.database, user=self.user, password=self.password) as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                         SELECT * FROM public.User
                         WHERE id = %s;
                         """, (id,))
                        user_infos = cur.fetchall()
                    conn.commit()
                conn.close()
                print(user_infos)
                if len(user_infos) > 0:
                    entry = user_infos[0]
                    user_info = VKUser(int(entry[0]), entry[1], entry[2], entry[3], entry[4], entry[5])
                    user_info.url = entry[6]
                    photos_dict = self.get_user_photos(id)
                    user_info.photos_dict = photos_dict
                    user_info_list.append(user_info)

        return user_info_list


# if __name__ == '__main__':
#     db_obj = DBObject('vkinder', 'postgres', '1234')
#     db_obj.create_user_db()







