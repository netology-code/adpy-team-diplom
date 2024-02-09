from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor, VkKeyboardButton
from sqlalchemy import create_engine
from db.orm import ORMvk
from db.create_db import create_tables
from datetime import date

DSN = f'перенёс временно из main'

engine = create_engine(DSN)

create_tables(engine)

personal_token = 'токен'
myORM = ORMvk(engine)
def filter_friends(partners_list):
    if not partners_list['is_friend'] and not partners_list['is_closed'] and len(partners_list['bdate']) > 8:
        return True
    else:
        return False

personal_vk = vk_api.VkApi(token=personal_token)
token = 'токен'
# token = input('Token: ')
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)
first_keyboard = VkKeyboard()
active_keyboard = VkKeyboard()


testers = None

def partners_gen(partners_list):
    for person in partners_list:
        yield person

class VkBot:
    def __init__(self, personal_vk_token, vk_token):
        self.vk = vk_api.VkApi(token=vk_token)
        self.testers = []
        self.personal_vk = personal_vk_token
        self.current_state = 0
        self.hometown = ''
        self.partner_age = 0

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
            best_images.append(f"photo{self.testers[0]['id']}_{image[1]}")
        return best_images

    def next_partner(self):
        if self.testers is None or not self.testers:
            self.testers = \
            self.personal_vk.method('users.search',
                                    values={'count': 1000, 'sex': 1, 'has_photo': 1,'hometown': self.hometown,'age_from': self.partner_age-2,'age_to': self.partner_age+2, 'fields': 'is_friend, sex, bdate'})['items']
        self.testers = list(filter(filter_friends,self.testers))
        for person in partners_gen(self.testers):
            print(person)
            myORM.add_partner(event.user_id, person['id'],
                              {'name': person['first_name'], 'surname': person['last_name'],
                               'gender': person['sex'],
                               'age': int(str(date.today())[:4]) - int(person['bdate'][-4:]), 'foto': self.get_photos(person), 'link': f'https://vk.com/id{person["id"]}'})
        # self.send_photos(event.user_id, attachment=",".join(self.get_photos()))     брать из БД будем
        self.write_msg(event.user_id, f'https://vk.com/id{self.testers[0]["id"]}')
        self.testers.pop(0)

    def send_photos(self, user_id, attachment):
        self.vk.method('messages.send', {'user_id': user_id, 'attachment': attachment, 'random_id': randrange(10 ** 7), })

    def write_msg(self,user_id, message):
        self.vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })

    def first_state(self):
        request = event.text
        if request == "начать":
            send_keyboard(event.user_id, 'Начинаем!', first_keyboard.get_keyboard())
        elif request == "привет":
            self.write_msg(event.user_id, f"Хай, {event.user_id}")
        elif request == "пока":
            self.write_msg(event.user_id, "Пока((")
        elif request.lower() == "подобрать":
            send_keyboard(event.user_id, 'Введите город для поиска', first_keyboard.get_empty_keyboard())
            # self.write_msg(event.user_id,'Введите город для поиска')
            self.current_state += 1
            # self.next_partner()
        else:
            self.write_msg(event.user_id, "Не поняла вашего ответа...")

    def second_state(self):
        request = event.text
        self.hometown = request
        print(self.hometown)
        self.write_msg(event.user_id, 'Введите возраст партнера')
        self.current_state += 1

    def third_state(self):
        request = event.text
        self.partner_age = int(request)
        print(self.partner_age)
        send_keyboard(event.user_id, 'Всё готово, можно начинать', active_keyboard.get_keyboard())
        self.current_state += 1

    def active_state(self):
        request = event.text
        if request.lower() == 'следующий':
            self.next_partner()
        elif request.lower() == 'назад':
            self.current_state = 0


vkbot = VkBot(personal_vk,token)


def send_keyboard(user_id, message, keyboard):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7),'keyboard': keyboard})

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
            myORM.add_user(vk_id=event.user_id,data={'age': 23, 'city': 'Москва', 'gender': 1})
            match vkbot.current_state:
                case 0:
                    vkbot.first_state()
                case 1:
                    vkbot.second_state()
                case 2:
                    vkbot.third_state()
                case 3:
                    vkbot.active_state()