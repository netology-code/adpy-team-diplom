import os
from random import randrange
from datetime import date

from vk_api import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor, VkKeyboardButton
from sqlalchemy import create_engine
from db.orm import ORMvk
from db.create_db import create_tables

from dotenv import load_dotenv, find_dotenv


class VkClass:
    def __init__(self, vk_personal, vk_group, orm):
        # self.vk = vk_api.VkApi(token=vk_token)
        self.vk_group = vk_group
        self.personal_vk = vk_personal
        self.orm = orm
        self.testers = []
        self.current_state = 0
        self.hometown = ''
        self.partner_age = 0
        self.partner_info = []

    def partners_gen(self, partners_list):
        for person in partners_list:
            yield person

    def filter_friends(self, partners_list):
        if not partners_list['is_friend'] and not partners_list['is_closed'] and len(partners_list['bdate']) > 8:
            return True
        else:
            return False

    def send_keyboard(self, user_id, message, keyboard):
        self.vk_group.method('messages.send',
                             {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7),
                              'keyboard': keyboard})

    def get_photos(self, person):
        all_photos = []
        for image in self.personal_vk.method('photos.get',
                                             {'owner_id': person['id'],
                                              'album_id': "profile", "extended": "1"})['items']:
            all_photos.append([image["likes"]["count"], image["id"]])
        all_photos.sort()
        all_photos.reverse()
        best_images = []
        for image in all_photos[:3]:
            best_images.append(f"photo{person['id']}_{image[1]}")
        return best_images

    def next_partner(self, event):
        if self.testers is None or not self.testers:
            self.testers = \
                self.personal_vk.method('users.search',
                                        values={'count': 20, 'sex': 1, 'has_photo': 1, 'hometown': self.hometown,
                                                'age_from': self.partner_age - 2, 'age_to': self.partner_age + 2,
                                                'fields': 'is_friend, sex, bdate'})['items']
        self.testers = list(filter(self.filter_friends, self.testers))
        for person in self.partners_gen(self.testers):
            print(person)
            self.orm.add_partner(event.user_id, person['id'],
                                 {'name': person['first_name'], 'surname': person['last_name'],
                                  'gender': person['sex'],
                                  'age': int(str(date.today())[:4]) - int(person['bdate'][-4:]),
                                  'foto': self.get_photos(person), 'link': f'https://vk.com/id{person["id"]}'})



    def send_photos(self, user_id,message, attachment):
        self.vk_group.method('messages.send',
                             {'user_id': user_id, 'message': message,'attachment': attachment, 'random_id': randrange(10 ** 7), })

    def write_msg(self, user_id, message):
        self.vk_group.method('messages.send',
                             {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })

    def first_state(self, event, first_keyboard):
        request = event.text
        if request.lower() == "начать":
            self.send_keyboard(event.user_id, 'Начинаем!', first_keyboard.get_keyboard())
        elif request.lower() == "показать избранное":
            for partner in self.orm.get_favorite_list(self.orm.get_user_id(event.user_id)):
                self.partner_info = self.orm.get_partner(partner)
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), self.partner_info[3][0])
        elif request.lower() == "показать заблокированных":
            for partner in self.orm.get_blacklist(self.orm.get_user_id(event.user_id)):
                self.partner_info = self.orm.get_partner(partner)
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), self.partner_info[3][0])
        elif request.lower() == "подобрать":
            self.send_keyboard(event.user_id, 'Введите город для поиска', first_keyboard.get_empty_keyboard())
            self.current_state += 1
        elif request.lower() == "автоподбор":

        else:
            self.write_msg(event.user_id, "Не поняла вашего ответа...")

    def second_state(self, event):
        request = event.text
        self.hometown = request
        print(self.hometown)
        self.write_msg(event.user_id, 'Введите возраст партнера')
        self.current_state += 1

    def third_state(self, event, active_keyboard):
        request = event.text
        self.partner_age = int(request)
        print(self.partner_age)
        self.next_partner(event)
        self.send_keyboard(event.user_id, 'Всё готово, можно начинать', active_keyboard.get_keyboard())
        self.partner_info = self.orm.get_random_partner()
        self.send_photos(event.user_id, ' '.join(self.partner_info[:3]),','.join(self.partner_info[3]))

        self.current_state += 1

    def active_state(self, event,first_keyboard):
        request = event.text
        if request.lower() == 'следующий':
            self.orm.clear_partner_row(self.orm.get_user_id(event.user_id))
            self.partner_info = self.orm.get_random_partner()
            self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
        elif request.lower() == 'назад':
            self.current_state = 0
            self.send_keyboard(event.user_id, 'Начинаем!', first_keyboard.get_keyboard())
        elif request.lower() == 'в избранное':
            self.orm.add_favorite(self.orm.get_last_user_id(self.orm.get_user_id(event.user_id)))
            self.partner_info = self.orm.get_random_partner()
            self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
        elif request.lower() == 'заблокировать':
            self.orm.add_blacklist(self.orm.get_last_user_id(self.orm.get_user_id(event.user_id)))
            self.partner_info = self.orm.get_random_partner()
            self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))

