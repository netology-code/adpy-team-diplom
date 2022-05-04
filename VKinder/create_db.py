import psycopg2
import psycopg2.extras

hostname = 'localhost'
database = 'vkinder'
username = 'postgres'
pwd = 'klubkik1970'
port_id = 5432
#connection = None

connection = psycopg2.connect(host=hostname, dbname=database, user=username, password=pwd, port=port_id)

with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:

    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('DROP TABLE IF EXISTS search_results')
    cursor.execute('DROP TABLE IF EXISTS favorites')

    create_script = ''' CREATE TABLE IF NOT EXISTS users(
                                user_id     int PRIMARY KEY,
                                token       varchar(50)
                                age         int NOT NULL,
                                gender      varchar(10) NOT NULL,
                                city        varchar(50) NOT NULL
                                ) '''
    cursor.execute(create_script)

    create_script = ''' CREATE TABLE IF NOT EXISTS partners(
                                partner_id  int PRIMARY KEY,
                                user_id     int,
                                first_name  varchar(50),
                                last_name   varchar(50),
                                age         int,
                                gender      varchar(10),
                                city        varchar(50),
                                profile_ref varchar(50),
                                photo_ref1  varchar(50)
                                photo_ref2  varchar(50)
                                photo_ref3  varchar(50)
                                ) '''
    cursor.execute(create_script)

    create_script = ''' CREATE TABLE IF NOT EXISTS favorites(
                                partner_id  int,
                                user_id     int 
                                ) '''
    cursor.execute(create_script)