from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor, VkKeyboardButton
from vkuser import VkDownload

import requests

# class VK:
#
#    def __init__(self, access_token, user_id, version='5.131'):
#        self.token = access_token
#        self.id = user_id
#        self.version = version
#        self.params = {'access_token': self.token, 'v': self.version}
#
#    def users_info(self):
#        url = 'https://api.vk.com/method/users.get'
#        params = {'user_ids': self.id}
#        response = requests.get(url, params={**self.params, **params})
#        return response.json()

user_id = '636054'
# vk = VK(access_token, user_id)
# print(vk.users_info())

#token = input('Token: ')
# token = 'vk1.a.pQaiq_hNnQyeqrG8KuLMvHUcoIfIRbIebzT9eBjc2eYh5h_v8DAORV2nXZ9pPhXBK0ZjxzDUOxj7SuG-6vOs5rPIswsVBTvlsFoydu6WvY_QBgm1gtQNlHtRvIGTjwUwnp914lh5u3GlWJo5iFLFr20Ks0qfyh8vDBF9j3-3ltrXHl2S88IbrQtPD-b_bddK'
# vk = vk_api.VkApi(token=token)
# longpoll = VkLongPoll(vk)
# keyboard = VkKeyboard()
# keyboard.add_button('next', VkKeyboardColor.PRIMARY)
# keyboard.add_button('favourites', VkKeyboardColor.POSITIVE)
# keyboard.add_button('blacklist', VkKeyboardColor.NEGATIVE)
# keyboard.add_button('lala', VkKeyboardColor.SECONDARY)
#
#
# def write_msg(user_id, message):
#     vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7), 'keyboard': keyboard.get_keyboard()})


# for event in longpoll.listen():
#     if event.type == VkEventType.MESSAGE_NEW:
#         if event.to_me:
#             request = event.text
#             print(f'request: {request}')
#             if request == "привет":
#                 print('привет')
#                 write_msg(event.user_id, f"Хай, {event.user_id}")
#             elif request == "пока":
#                 print('пока')
#                 write_msg(event.user_id, "Пока((")
#             else:
#                 print('не понял')
#                 print(f'{event.user_id}')
#                 write_msg(event.user_id, "Не поняла вашего ответа...")

if __name__ == '__main__':
    vkd = VkDownload()
    user = vkd.get_user_info(user_id)
    vkd.find_possible_pairs(user)
