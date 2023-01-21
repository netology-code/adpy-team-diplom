import vk_api
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import cities
from config import token_for_bot, token_for_app
from app.app_for_searching import VK
import time
# if __name__ == '__main__':


def test(user_id):
    id_of_user = user_id
    return str(id_of_user)


def send_mes(text):
    session_api.messages.send(
        random_id=get_random_id(),
        message=text,
        user_id=event.message.from_id
    )


def registration(user_id, city):
    vk = VK(access_token=token_for_app, user_id=test(user_id))
    info = vk.users_info()
    url = "https://vk.com/id{}".format(user_id)
    for values in info.values():
        dict_of_info = values[0]
        if dict_of_info['is_closed'] == True:
            send_mes('Открой профиль, и возобнови регистрацию')
        else:
            send_mes('Регистрация закончена')


vk_session = vk_api.VkApi(token=token_for_bot)
session_api = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, 218368602)
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        user_id = str(event.message.from_id)
        if 'Регистрация' in event.message.text:
            send_mes('Введите город в котором хотите искать людей')
        if event.message.text in cities.city:
            city = event.message.text
            registration(user_id, city)
        # if 'Покажи мне анкету' in event.message.text:
        #     send_mes('я')
        #     print(vk.pars_photo(vk=vk))

