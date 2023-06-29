import os
from dotenv import load_dotenv
from database.models import Base


class Database:
    def __init__(self):
        dotenv_path = os.path.join(os.path.dirname(__file__), ".envrc")
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
        self.bd = os.getenv("bd")
        self.bd_port = os.getenv("bd_port")
        self.bd_name = os.getenv("bd_name")
        self.bd_username = os.getenv("bd_username")
        self.bd_pass = os.getenv("bd_pass")
        self.file_name = os.getenv("file_name")
        self.bd_localhost = os.getenv("localhost")

    def create_conect(self):
        dsn = "{}://{}:{}@{}:{}/{}".format(
            self.bd,
            self.bd_username,
            self.bd_pass,
            self.bd_localhost,
            self.bd_port,
            self.bd_name,
        )
        return dsn

    def create_tables(self, engine):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
