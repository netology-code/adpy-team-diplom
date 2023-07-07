from random import randrange
import request
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

token = input('Token: vk1.a.MJyGvsT2LdL5icKXxEKwK9pWg0THICZYNOGvu7mTnOBGMhX3JZCWO7k7gUbyXcr6zOXWNMQKi6LnStUvDal2YR1j8ClvEcawJ4WAOZXxn6NogdHIaFQegADc4zpXImty1iAUb16lvbsClTud536JaOBhH6MLk27hQ0F8hL7lB1FMp0eKFi6lJ4XnUhzjbouZkU5HZ7NaoATtqF_EXmMVOg')

vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if request == "привет":
                write_msg(event.user_id, f"Хай, {event.user_id}")
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")
