from db_manager import DBObject
import psycopg2

class DBConnection:
    cur = None
    conn = None
    def __init__(self, db_obj: DBObject):
        self.db_obj = db_obj

    def open_connection(self):
        with psycopg2.connect(database=self.db_obj.database, user=self.db_obj.user, password=self.db_obj.password) as conn:
            with conn.cursor() as cur:
                self.db_obj.create_user_db(cur)
                self.cur = cur
                self.conn = conn
        return cur

    def commit_request(self):
        self.conn.commit()

    def close_connection(self):
        self.conn.close()


