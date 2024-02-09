from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor, VkKeyboardButton
from sqlalchemy import create_engine
from db.orm import ORMvk
from db.create_db import create_tables

DSN = f'postgresql://postgres:201224@localhost:5432/vkinder'

engine = create_engine(DSN)

create_tables(engine)

personal_token = 'vk1.a.N7DJW9j7Q9TLUBuzGdFHNKrEaHc1S3VUSeRdC9a-v11Cltud98VuO3gLoBhMTr0QGUNYWHiKqViavFSRmS_bkRXYNoCXDXfB6eDJZuMyhwa5-QpzjTswaPmCzLgQDCn5M-BMO3LOT_PtMGOs2xQzy0IxMUHjdVds9dBDT2fNUdt-5CIaSIlUHGDcThD-lhjR'
myORM = ORMvk(engine)
def filter_friends(partners_list):
    if not partners_list['is_friend'] and not partners_list['is_closed']:
        return True
    else:
        return False

personal_vk = vk_api.VkApi(token=personal_token)
token = 'vk1.a.tJsBcxT5vZEq8eIh-VMmuhJDeWdEoUm5Ziz8Mg524f-0CSIW7Bi4xXkHQLUeBdhXuv6n8A19umgV3onwGodtHrxnGt6mrvhjQQOPWPUSBrbbC0mgL9IKPmYJHsD1CS8B_7NRW9d5qabSxG3AAsHEbdj7iRGFFrXEDEQE1gocE2YYj9iLbby8RFI3-Nwflocrd9llPrW1k6EvLW774A-FpA'
# token = input('Token: ')
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)
first_keyboard = VkKeyboard()
active_keyboard = VkKeyboard()


testers = None


class VkBot:
    def __init__(self, personal_vk_token, vk_token):
        self.vk = vk_api.VkApi(token=vk_token)
        self.testers = []
        self.personal_vk = personal_vk_token
        self.current_state = 0
        self.hometown = ''
        self.partner_age = 0

    def next_partner(self):
        if self.testers is None or not self.testers:
            self.testers = \
            self.personal_vk.method('users.search',
                                    values={'count': 100, 'sex': 1, 'has_photo': 1,'hometown': self.hometown,'age_from': self.partner_age-1,'age_to': self.partner_age+1, 'fields': ['is_friend']})['items']
        self.testers = list(filter(filter_friends,self.testers))
        all_photos = []
        for image in self.personal_vk.method('photos.get',
                                   {'owner_id': self.testers[0]['id'],
                                    'album_id': "profile", "extended": "1"})['items']:
            all_photos.append([image["likes"]["count"], image["id"]])
        all_photos.sort()
        all_photos.reverse()
        best_images = []
        for image in all_photos[:3]:
            best_images.append(f"photo{self.testers[0]['id']}_{image[1]}")
        self.send_photos(event.user_id, attachment=",".join(best_images))
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
#vkkeyboard.add_button('Следующий', VkKeyboardColor.PRIMARY)
first_keyboard.add_line()
#vkkeyboard.add_button('В избранное', VkKeyboardColor.PRIMARY)
first_keyboard.add_button('Показать избранное', VkKeyboardColor.PRIMARY)
#vkkeyboard.add_button('Заблокировать', VkKeyboardColor.PRIMARY)
#vkkeyboard.add_line()
first_keyboard.add_button('Показать заблокированных', VkKeyboardColor.PRIMARY)
#vkkeyboard.add_button('Лайк', VkKeyboardColor.PRIMARY)
#vkkeyboard.add_button('Дизлайк', VkKeyboardColor.PRIMARY)

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