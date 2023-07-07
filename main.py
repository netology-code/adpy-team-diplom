from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

token = "vk1.a.LsZtw3AbYwfIWCAr12ruoEZ-4IKESSQlL8bVTQA4Epj3uByM5HAq_dWWaWTlWfcqXcaL8IpQuNbqbhQymDb5dL3dq8-jXnKuqKCgPA4M-o29K-d2yOxyY63V1oZPD61qaRAO7xbsBkqjoaocdxu78KT9MrGs63iIXDVVjIKGan_MqAnn1JYnF8W74q2X8fNSbFwOyMulGavqyAd8pofCTg"

vk = vk_api.VkApi(token=token)
session_api = vk.get_api()
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if request == "привет":
                user_info = session_api.users.get(user_ids=(event.user_id))
                print(user_info)
                user_info = user_info[0]
                write_msg(event.user_id, f"Хай, {event.user_id}, или по вашему {user_info['last_name']} {user_info['first_name']}")
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")
