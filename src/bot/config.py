from os import getenv

from dotenv import load_dotenv
from vkbottle import Bot, CtxStorage

from src.database.database_interface import DatabaseInterface


load_dotenv()

TOKEN = getenv("TOKEN")

BOT = Bot(TOKEN)

CTX = CtxStorage()

DB = DatabaseInterface()
