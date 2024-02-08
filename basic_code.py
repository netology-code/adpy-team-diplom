from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor, VkKeyboardButton


personal_token = 'Ваш токен'

def filter_friends(partners_list):
    if not partners_list['is_friend'] and not partners_list['is_closed']:
        return True
    else:
        return False

personal_vk = vk_api.VkApi(token=personal_token)
token = 'токен сообщества'
# token = input('Token: ')
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)
vkkeyboard = VkKeyboard()

testers = None


class VkBot:
    def __init__(self, personal_vk_token, vk_token):
        self.vk = vk_api.VkApi(token=vk_token)
        self.testers = []
        self.personal_vk = personal_vk_token

    def next_partner(self):
        if self.testers is None or not self.testers:
            self.testers = \
            self.personal_vk.method('users.search',
                                    values={'count': 100, 'sex': 1, 'has_photo': 1, 'fields': ['is_friend']})['items']
        self.testers = list(filter(filter_friends,self.testers))
        all_photos = []
        for image in self.personal_vk.method('photos.get',
                                   {'owner_id': self.testers[-1]['id'],
                                    'album_id': "profile", "extended": "1"})['items']:
            all_photos.append([image["likes"]["count"], image["id"]])
        all_photos.sort()
        all_photos.reverse()
        best_images = []
        for image in all_photos[:3]:
            best_images.append(f"photo{self.testers[-1]['id']}_{image[1]}")
        self.send_photos(event.user_id, attachment=",".join(best_images))
        self.testers.pop()

    def send_photos(self, user_id, attachment):
        self.vk.method('messages.send', {'user_id': user_id, 'attachment': attachment, 'random_id': randrange(10 ** 7), })

    def write_msg(self,user_id, message):
        self.vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })


vkbot = VkBot(personal_vk,token)


def send_keyboard(user_id, message, keyboard):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7),'keyboard': keyboard})

vkkeyboard.add_button('Подобрать', VkKeyboardColor.PRIMARY)
vkkeyboard.add_button('Автоподбор', VkKeyboardColor.PRIMARY)
vkkeyboard.add_button('Следующий', VkKeyboardColor.PRIMARY)
vkkeyboard.add_line()
vkkeyboard.add_button('В избранное', VkKeyboardColor.PRIMARY)
vkkeyboard.add_button('Показать избранное', VkKeyboardColor.PRIMARY)
vkkeyboard.add_button('Заблокировать', VkKeyboardColor.PRIMARY)
vkkeyboard.add_line()
vkkeyboard.add_button('Показать заблокированных', VkKeyboardColor.PRIMARY)
vkkeyboard.add_button('Лайк', VkKeyboardColor.PRIMARY)
vkkeyboard.add_button('Дизлайк', VkKeyboardColor.PRIMARY)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text
            if request == "начать":
                send_keyboard(event.user_id, 'Начинаем!', vkkeyboard.get_keyboard())
            elif request == "привет":
                vkbot.write_msg(event.user_id, f"Хай, {event.user_id}")
            elif request == "пока":
                vkbot.write_msg(event.user_id, "Пока((")
            elif request == "подобрать":
                vkbot.next_partner()
            else:
                vkbot.write_msg(event.user_id, "Не поняла вашего ответа...")
