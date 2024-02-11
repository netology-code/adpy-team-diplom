import os

from sqlalchemy import create_engine
from dotenv import load_dotenv, find_dotenv

from db.orm import ORMvk
from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor, VkKeyboardButton

from db.create_db import create_tables
from datetime import date
from vkinder.vk_bot import VkBot

if __name__ == '__main__':
    load_dotenv(find_dotenv(),encoding='latin-1')

    LOGIN = os.environ.get('LOGIN')
    PSW = os.environ.get('PSW')
    HOST = os.environ.get('HOST')
    PORT = os.environ.get('PORT')
    NAMEDB = os.environ.get('NAMEDB')
    PERSONALTOKEN = os.environ.get('VKCLIENTS')
    GROUP_TOKEN = os.environ.get('VK_TOKEN_GROUP')

    # url_database = os.getenv('URL_DATABASE')

    DSN = f'postgresql://{LOGIN}:{PSW}@{HOST}:{PORT}/{NAMEDB}'

    vk = vk_api.VkApi(token=GROUP_TOKEN)

    vk_bot = VkBot(ORMvk(create_engine(DSN)), GROUP_TOKEN, PERSONALTOKEN)
    vk_bot.run_bot()


