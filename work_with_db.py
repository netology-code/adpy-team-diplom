import psycopg2
import configparser
from pprint import pprint


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
        try:
            column_name = [el for el in dict_.keys()]
            value = [el for el in dict_.values()]
            s = ', '.join(['%s'] * len(dict_))
            conn = self.connect()
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
            return

    def select(self, table_name: str):
        try:
            conn = self.connect()
            with conn.cursor() as cur:
                cur.execute(f'''
                SELECT
                    peoples.peoples_id, id_vk, first_name, last_name, city, sex
                FROM
                    peoples
                JOIN
                    {table_name} on peoples.peoples_id = {table_name}.peoples_id;
                ''')
                response = ('fetchall', cur.fetchall())
            conn.close()
            return response[1]
        except:
            return

    def get_all(self):
        try:
            conn = self.connect()
            with conn.cursor() as cur:
                cur.execute(f'''
                SELECT 
                    * 
                FROM 
                    {self.table_name};
                ''')
                response = ('fetchall', cur.fetchall())
            conn.close()
            return response[1]
        except:
            return

    def search_name(self, first_name: str, last_name: str):
        try:
            conn = self.connect()
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
                response = ('fetchall', cur.fetchall())
            conn.close()
            return response[1]
        except:
            return

    def search_age(self, start=0, stop=100):
        try:
            conn = self.connect()
            with conn.cursor() as cur:
                cur.execute(f'''
                SELECT 
                    * 
                FROM 
                    {self.table_name}
                WHERE 
                    age between %s and %s;
                ''', (start, stop))
                response = ('fetchall', cur.fetchall())
            conn.close()
            return response[1]
        except:
            return

    def search_city(self, city: str):
        try:
            conn = self.connect()
            with conn.cursor() as cur:
                cur.execute(f'''
                SELECT 
                    * 
                FROM 
                    {self.table_name}
                WHERE 
                    city = %s;
                ''', (city,))
                response = ('fetchall', cur.fetchall())
            conn.close()
            return response[1]
        except:
            return

    def search_sex(self, sex: str):
        try:
            conn = self.connect()
            with conn.cursor() as cur:
                cur.execute(f'''
                SELECT 
                    * 
                FROM 
                    {self.table_name}
                WHERE 
                    sex = %s;
                ''', (sex,))
                response = ('fetchall', cur.fetchall())
            conn.close()
            return response[1]
        except:
            return

    def search_all_parameters(
            self, first_name: str, last_name: str, city: str, sex: str,
            min_age=0, max_age=100
    ):
        try:
            conn = self.connect()
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
                response = ('fetchall', cur.fetchall())
            conn.close()
            return response[1]
        except:
            return

    def check(self, peoples_id: int, table_name: str):
        check_list = [el[0] for el in self.select(table_name)]
        if peoples_id in check_list:
            return False
        else:
            return True

    def get_id(self, first_name: str, last_name: str):
        people_id = self.search_name(first_name, last_name)
        if len(people_id) > 1:
            people_id = [id_[0] for id_ in people_id]
            return people_id
        else:
            return people_id

    def delete(self, people_id):
        try:
            conn = self.connect()
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

    def insert(self, peoples_id):
        if self.check(peoples_id, 'black_list'):
            dict_ = {'peoples_id': f'{peoples_id}'}
            try:
                column_name = [el for el in dict_.keys()]
                value = [el for el in dict_.values()]
                s = ', '.join(['%s'] * len(dict_))
                conn = self.connect()
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
                return
        else:
            print(
                'Невозможно добавить в избранное, человек находится в чёрном '
                'списке.'
            )
            return


class BlackList(Peoples):

    def __init__(self):
        super().__init__()
        self.table_name = 'black_list'
        self.column_name = 'peoples_id'

    def insert(self, peoples_id):
        if self.check(peoples_id, 'favorite_people'):
            dict_ = {'peoples_id': f'{peoples_id}'}
            try:
                column_name = [el for el in dict_.keys()]
                value = [el for el in dict_.values()]
                s = ', '.join(['%s'] * len(dict_))
                conn = self.connect()
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
                return
        else:
            print(
                'Невозможно добавить в чёрный список, человек находится '
                'в избранном.'
            )


if __name__ == '__main__':
    peoples = Peoples()
    photos = Photos()
    favorite_people = Favorite()
    black_list = BlackList()

    # добавим нового человека.
    candidate = {
        'id_vk': 1, 'first_name': 'Grisha', 'last_name': 'Petrov',
        'age': 45, 'city': 'Москва', 'sex': 'male'
    }

    links = ['https://...', 'https://....', 'https://.....']

    # загрузим данные в БД
    peoples.insert(candidate)
    id_ = candidate.get('id_vk')
    # здесь берем именно id_vk так как он является уникальным в отличие от
    # имени и фамилии
    for link in links:
        photo = {'link': link, 'peoples_id': id_}
        photos.insert(photo)

    # добавим человека в избранный список для этого нужно получить id
    # если есть два человека с одинаковым именем и фамилией, тогда вернётся
    # список с id необходимо запросить у пользователя доп параметры.
    id_ = peoples.get_id('Grisha', 'Petrov')
    print(id_)
    favorite_people.insert(id_)

    # добавим человека в чёрный список.
    id_ = peoples.get_id('Grisha', 'Petrov')
    black_list.insert(id_)

    # поиск по имени
    pprint(peoples.search_name('Grisha', 'Petrov'))
    print()

    # выборка по возрасту
    pprint(peoples.search_age(21, 35))
    print()

    # выборка по городу
    pprint(peoples.search_city('SPB'))
    print()

    # выборка по полу
    pprint(peoples.search_sex('famale'))
    print()

    # удалить из избранного списка
    id_ = peoples.get_id('Grisha', 'Petrov')
    favorite_people.delete(id_)

    # удалить из чёрного списка
    id_ = peoples.get_id('Grisha', 'Petrov')
    black_list.delete(id_)

    # удалить из общего списка
    id_ = peoples.get_id('Grisha', 'Petrov')
    peoples.delete(id_)

    # получить всех пользоватлей
    pprint(peoples.get_all())

    # выборка по всем параметрам
    pprint(peoples.search_all_parameters(
        'Grisha', 'Petrov', 'Москва', 'male', 18, 46
    ))
