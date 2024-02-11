from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor, VkKeyboardButton
from sqlalchemy import create_engine
from db.orm import ORMvk
from db.create_db import create_tables
from datetime import date
from dotenv import load_dotenv, find_dotenv
import os
from vkinder.vk_class import VkClass

load_dotenv(find_dotenv())

testers = None


class VkBot:
    def __init__(self, orm, group_token, personal_token):
        self.orm = orm
        self.group_token = group_token
        self.personal_token = personal_token

    def check_db(self):
        ORMvk.check_database(self.orm)

    def create_vk_group(self):
        return vk_api.VkApi(token=self.group_token)

    def create_vk_personal(self):
        return vk_api.VkApi(token=self.personal_token)

    def create_vkbot(self):
        return VkClass(self.create_vk_personal(), self.create_vk_group(), self.orm)

    def run_bot(self):
        self.check_db()

        first_keyboard = VkKeyboard()
        active_keyboard = VkKeyboard()
        longpoll = VkLongPoll(self.create_vk_group())
        vkbot = self.create_vkbot()

        first_keyboard.add_button('Подобрать', VkKeyboardColor.PRIMARY)
        first_keyboard.add_button('Автоподбор', VkKeyboardColor.PRIMARY)
        first_keyboard.add_line()
        first_keyboard.add_button('Показать избранное', VkKeyboardColor.PRIMARY)
        first_keyboard.add_button('Показать заблокированных', VkKeyboardColor.PRIMARY)

        active_keyboard.add_button('Следующий', VkKeyboardColor.PRIMARY)
        active_keyboard.add_button('Назад', VkKeyboardColor.PRIMARY)
        active_keyboard.add_line()
        active_keyboard.add_button('В избранное', VkKeyboardColor.PRIMARY)
        active_keyboard.add_button('Заблокировать', VkKeyboardColor.PRIMARY)
        active_keyboard.add_line()
        active_keyboard.add_button('Лайк', VkKeyboardColor.PRIMARY)
        active_keyboard.add_button('Дизлайк', VkKeyboardColor.PRIMARY)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    self.orm.add_user(vk_id=event.user_id, data={'age': 23, 'city': 'Москва', 'gender': 1})
                    match vkbot.current_state:
                        case 0:
                            vkbot.first_state(event, first_keyboard)
                        case 1:
                            vkbot.second_state(event)
                        case 2:
                            vkbot.third_state(event, active_keyboard)
                        case 3:
                            vkbot.active_state(event)

