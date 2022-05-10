import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def connect_to_db():
    hostname = 'localhost'
    database = 'postgres'
    username = 'postgres'
    pwd = '***'
    port_id = 5432
    connection = psycopg2.connect(host=hostname, dbname=database, user=username, password=pwd, port=port_id)
    return connection

def execute_sql(sql_script: str, returnResults: bool):
    connection = connect_to_db()
    try:
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()
        cursor.execute(sql_script)
        if returnResults:
            return cursor.fetchall()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()

def add_new_user_to_db(user_info: dict):
    insert_script = f'''INSERT INTO users VALUES(
    '{user_info["user_id"]}',
    '{user_info["user_token"]}',
    {user_info["age"]},
    '{user_info["gender"]}',
    '{user_info["city"]}'
    )'''
    execute_sql(insert_script, False)

def get_user_data_from_db(user_id: str):
    select_script = f"SELECT * FROM users WHERE user_id = '{user_id}'"
    res = execute_sql(select_script, True)[0]
    return {'user_id': res[0], 'user_token': res[1], 'age': res[2], 'gender': res[3], 'city': res[4]}

def add_to_favorites(user_id: str, partner_data: dict):
    insert_script_favorites = f'''INSERT INTO favorites VALUES(
    '{partner_data["partner_id"]}',
    '{user_id}'
    )'''
    execute_sql(insert_script_favorites, False)
    insert_script_partners = f'''INSERT INTO partners VALUES(
    '{partner_data["partner_id"]}',
    '{partner_data["first_name"]}',
    '{partner_data["last_name"]}',
    {partner_data["age"]},
    '{partner_data["gender"]}',
    '{partner_data["city"]}',
    '{partner_data["photo_ref1"]}',
    '{partner_data["photo_ref2"]}',
    '{partner_data["photo_ref3"]}'
    )'''
    execute_sql(insert_script_partners, False)

def display_favorites(user_id: str):
    sql_script = f'''SELECT partners.partner_id, first_name, last_name, age, gender, city
    FROM partners
    JOIN favorites ON favorites.partner_id = partners.partner_id
    WHERE favorites.user_id = '{user_id}'
    '''
    return execute_sql(sql_script, True)