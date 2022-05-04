import psycopg2
import psycopg2.extras

def connect_to_db():
    hostname = 'localhost'
    database = 'vkinder'
    username = 'postgres'
    pwd = '***'
    port_id = 5432
    connection = psycopg2.connect(host=hostname, dbname=database, user=username, password=pwd, port=port_id)
    return connection

def user_authorized(user_id):
    connection = connect_to_db()
    with connection.cursor() as cursor:
        select_script = f'SELECT * FROM users WHERE user_id = {user_id}'
        if len(cursor.execute(select_script)) == 0:
            return True
        else:
            return False

def add_new_user(age, gender, city):
    connection = connect_to_db()
    with connection.cursor() as cursor:
        insert_script = f'INSERT INTO users(age, gender, city) VALUES({age}, {gender}, {city}) RETURNING user_id'
        cursor.execute(insert_script)
        result = cursor.fetchall()
        print(f'User added to table users')
    return result[0]  # ??????

def get_user_info(user_id):
    connection = connect_to_db()
    with connection.cursor() as cursor:
        select_script = f'SELECT age, gender, city FROM users WHERE user_id = {user_id}'
        cursor.execute(select_script)
        result = cursor.fetchall()
        return {'age': result[0], 'gender': result[1], 'city': result[2]}

def add_to_favorites(partner_id, user_id):
    connection = connect_to_db()
    with connection.cursor() as cursor:
        insert_script = f'INSERT INTO favorites(user_id, partner_id) VALUES({user_id}, {partner_id})'
        cursor.execute(insert_script)
        print(f'Partner added to favorites')

def display_favorites(user_id):
    connection = connect_to_db()
    with connection.cursor() as cursor:
        select_script = f'SELECT * FROM favorites JOIN partners ON partners.user_id = favorites.{user_id}'
        cursor.execute(select_script)
        for record in cursor.fetchall():
            print(record[0], record[1], record[2], record[3], record[4] )

def add_partner_list_to_db(user_info):
    pass