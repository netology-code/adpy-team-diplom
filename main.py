import vk_api
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from config import token_for_bot, token_for_app
from app.registration import VKRegistration
from app.get_info import VkForParsInfo
# if __name__ == '__main__':


def test(user_id): # она нужна была мне для того, чтобы передавать юзер айди в другой модуль
    id_of_user = user_id
    return str(id_of_user)


def send_mes(text): #функция отправки сообщений ботом, чтобы каждый раз не писать в коде
    session_api.messages.send(
        random_id=get_random_id(),
        message=text,
        user_id=event.message.from_id
    )


def registration(user_id): # функция регистрации, которая будет вызывать модуль регистрации, и получать инфу для базы данныы.
    vk = VKRegistration(access_token=token_for_app, user_id=test(user_id))
    info = vk.users_info()
    url = "https://vk.com/id{}".format(user_id)

# тут всё для самого бота чтобы он запустился.
vk_session = vk_api.VkApi(token=token_for_bot)
session_api = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, 218368602)
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:  # сама логика бота, если сообщение новое, то начинается отработка событий
        user_id = str(event.message.from_id)
        vk = VkForParsInfo(access_token=token_for_app) # этим я просто проверял, как работает создание списка людей которых мне должно выдавать, в финале это будет выглядеть иначе.
        vk.users_get_free(sex='1', get_city='Казань')
        if 'Регистрация' in event.message.text:
            registration(user_id)
            # send_mes('Введите город в котором хотите искать людей')
        # if event.message.text in cities.city:
        #     city = event.message.text


        # if 'Покажи мне анкету' in event.message.text:
        #     send_mes('я')

