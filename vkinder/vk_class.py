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

from threading import Thread


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
        self.partner_gender = 1

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

    def next_partner(self, event,count,age):
        if self.testers is None or not self.testers:
            self.testers = \
                self.personal_vk.method('users.search',
                                        values={'count': count, 'sex': self.partner_gender, 'has_photo': 1, 'hometown': self.hometown,
                                                'age_from': age, 'age_to': age,
                                                'fields': 'is_friend, sex, bdate'})['items']
        self.testers = list(filter(self.filter_friends, self.testers))

        for person in self.partners_gen(self.testers):
            if len(self.get_photos(person)) < 3:
                continue
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

    def first_state(self, event, first_keyboard,active_keyboard):
        request = event.text
        if request.lower() == "начать":
            self.send_keyboard(event.user_id, 'Начинаем!', first_keyboard.get_keyboard())
        elif request.lower() == "показать избранное":
            for partner in self.orm.get_favorite_list(self.orm.get_user_id(event.user_id)):
                self.partner_info = self.orm.get_partner(partner)
                print(self.partner_info)
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), self.partner_info[3][0])
        elif request.lower() == "показать заблокированных":
            for partner in self.orm.get_blacklist(self.orm.get_user_id(event.user_id)):
                self.partner_info = self.orm.get_partner(partner)
                print(self.partner_info)
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), self.partner_info[3][0])
        elif request.lower() == "подобрать":
            self.send_keyboard(event.user_id, 'Введите город для поиска', first_keyboard.get_empty_keyboard())
            self.current_state += 1
            self.orm.add_state(event.user_id, 1)
        elif request.lower() == "автоподбор":
            print('auto')
            searh_data = self.orm.get_search_data(event.user_id)
            self.partner_age = searh_data[0]
            self.partner_gender = searh_data[1]
            self.hometown = searh_data[2]
            self.next_partner(event)
            self.send_keyboard(event.user_id, 'Всё готово, можно начинать', active_keyboard.get_keyboard())
            self.partner_info = self.orm.get_random_partner()
            self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
            self.current_state = 3
            self.orm.add_state(event.user_id, 3)
        else:
            self.write_msg(event.user_id, "Не поняла вашего ответа...")

    def second_state(self, event):
        request = event.text
        self.hometown = request
        print(self.hometown)
        self.write_msg(event.user_id, 'Введите возраст партнера')
        self.current_state += 1
        self.orm.add_state(event.user_id, 2)

    def third_state(self, event, active_keyboard):
        request = event.text
        self.partner_age = int(request)
        print(self.partner_age)

        import datetime

        # фиксируем и выводим время старта работы кода
        start = datetime.datetime.now()
        print('Время старта: ' + str(start))

        # код, время работы которого измеряем

        # фиксируем и выводим время окончания работы кода
        finish = datetime.datetime.now()
        print('Время окончания: ' + str(finish))

        # вычитаем время старта из времени окончания
        print('Время работы: ' + str(finish - start))
        Thread(target=self.next_partner, args=(event, 1000,self.partner_age-1)).start()
        Thread(target=self.next_partner, args=(event, 1000,self.partner_age)).start()
        Thread(target=self.next_partner, args=(event, 1000,self.partner_age+1)).start()
        self.next_partner(event, 25,self.partner_age)
        # фиксируем и выводим время окончания работы кода
        finish = datetime.datetime.now()
        print('Время окончания: ' + str(finish))

        # вычитаем время старта из времени окончания
        print('Время работы: ' + str(finish - start))
        self.send_keyboard(event.user_id, 'Всё готово, можно начинать', active_keyboard.get_keyboard())
        self.partner_info = self.orm.get_random_partner()
        self.send_photos(event.user_id, ' '.join(self.partner_info[:3]),','.join(self.partner_info[3]))
        self.current_state += 1
        self.orm.add_state(event.user_id, 3)

    def fourth_state(self, event, first_keyboard):
        request = event.text
        user_age = int(request)
        user_data = self.personal_vk.method(method='users.get',
                                             values={'user_ids': event.user_id, 'fields': 'sex,city,bdate'})
        self.orm.add_user(vk_id=event.user_id,
                          data={'age': user_age, 'city': user_data[0]['city']['title'],
                                'gender': user_data[0]['sex']})
        self.send_keyboard(event.user_id, 'Начинаем!', first_keyboard.get_keyboard())
        self.current_state = 0
        self.orm.add_state(event.user_id, 0)

    def active_state(self, event,first_keyboard):
        request = event.text
        if request.lower() == 'следующий':
            self.orm.clear_partner_row(self.orm.get_user_id(event.user_id))
            self.partner_info = self.orm.get_random_partner()
            if self.partner_info is None:
                self.next_partner(event)
                self.partner_info = self.orm.get_random_partner()
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
            else:
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
        elif request.lower() == 'выйти':
            self.orm.add_state(event.user_id,0)
            self.current_state = 0
            self.send_keyboard(event.user_id, 'Начинаем!', first_keyboard.get_keyboard())
        elif request.lower() == 'в избранное':
            self.orm.add_favorite(self.orm.get_last_user_id(self.orm.get_user_id(event.user_id)))
            self.partner_info = self.orm.get_random_partner()
            if self.partner_info is None:
                self.next_partner(event)
                self.partner_info = self.orm.get_random_partner()
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
            else:
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
        elif request.lower() == 'заблокировать':
            self.orm.add_blacklist(self.orm.get_last_user_id(self.orm.get_user_id(event.user_id)))
            self.partner_info = self.orm.get_random_partner()
            if self.partner_info is None:
                self.next_partner(event)
                self.partner_info = self.orm.get_random_partner()
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
            else:
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
