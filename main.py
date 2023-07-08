from random import randrange
from datetime import date
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import re

token = "vk1.a.LsZtw3AbYwfIWCAr12ruoEZ-4IKESSQlL8bVTQA4Epj3uByM5HAq_dWWaWTlWfcqXcaL8IpQuNbqbhQymDb5dL3dq8-jXnKuqKCgPA4M-o29K-d2yOxyY63V1oZPD61qaRAO7xbsBkqjoaocdxu78KT9MrGs63iIXDVVjIKGan_MqAnn1JYnF8W74q2X8fNSbFwOyMulGavqyAd8pofCTg"

vk = vk_api.VkApi(token=token)
session_api = vk.get_api()
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})

def get_info(user_id):
    user_info = session_api.users.get(user_ids=(user_id), fields=('city', 'sex', 'bdate'))
    user_info = user_info[0]
    birthday = user_info['bdate']
    pattern_age = r'(\d+)\.(\d+)\.(\d{4})'
    if re.match(pattern_age, birthday):
        today = date.today()
        age = today.year - int(re.sub(pattern_age, r'\3', birthday)) - ((today.month, today.day) < (int(re.sub(pattern_age, r'\2', birthday)), int(re.sub(pattern_age, r'\1', birthday))))
    else:
        age = 'Одному богу известно сколько'

    user_info = {
        'first_name': user_info['first_name'],
        'last_name': user_info['last_name'],
        'city': user_info['city']['title'],
        'age': age
    }

    return user_info


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if request == "привет":
                info_user = get_info(event.user_id)
                write_msg(event.user_id, f"Хай, {info_user['last_name']} {info_user['first_name']}, проживающий в городе {info_user['city']}")
                write_msg(event.user_id, f"Тебе {info_user['age']} лет")

            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")
