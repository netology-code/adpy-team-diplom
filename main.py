import json
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv
import os
import VK.vk_massages as ms
from User import User
from VK.VKService import VKService

load_dotenv()

token = os.getenv(key='ACCESS_TOKEN')
vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session)
users_list = {}


def handle_start(event_arg):
    user_id = event_arg.user_id
    if not user_id in users_list.keys():
        user = User(user_id)
        users_list[user_id] = user
        #users_info = vk_srv.get_users_info(vk_session, user.get_user_id())
        users_info = vk_srv.get_users_info(token=os.getenv(key='ACCESS_TOKEN_API'), user_id=user.get_user_id())
        if not users_info is None:
            user.set_first_name(users_info['first_name'])
            user.set_last_name(users_info['last_name'])
            user.set_gender(users_info['sex'])
            user.set_age(vk_srv.determine_age(users_info['bdate']))
            user.set_city(users_info['city'])
            hello_message = ms.get_hello_massage(user.get_user_id(), user.get_first_name())
            send_message(hello_message)
        else:
            hello_massage_error = ms.get_hello_massage_error(user.get_user_id())
            send_message(hello_massage_error)


def handle_registration(user):
    if user.get_id_msg_edit_anketa() > -1:
        vk_session.method('messages.delete', {'message_ids': user.get_id_msg_edit_anketa(), 'delete_for_all': 1})
    message_registration = ms.get_registration_massage(user)
    return send_message(message_registration)


def send_ask_edit(user_id, str_arg):
    message_edit = ms.get_edit_massage(user_id, str_arg)
    send_message(message_edit)


def send_message(message):
    return vk_session.method('messages.send', message)


if __name__ == '__main__':
    vk_srv = VKService()
    for event in VkLongPoll(vk_session).listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            text = event.text.lower()
            if text == 'start':
                handle_start(event)
            elif text == 'хочу зарегистрироваться':
                message_id = handle_registration(users_list[event.user_id])
                users_list[event.user_id].set_id_msg_edit_anketa(message_id)
            elif event.extra_values.get('payload'):
                if json.loads(event.extra_values.get('payload')).get('action_edit'):
                    str_arg = json.loads(event.extra_values.get('payload')).get('action_edit')
                    send_ask_edit(event.user_id, str_arg)
                elif json.loads(event.extra_values.get('payload')).get('action_save'):
                    s = ''
                elif json.loads(event.extra_values.get('payload')).get('action_cancel'):
                    if json.loads(event.extra_values.get('payload')).get('action_cancel') == 'cancel_edit_anketa':
                        message_id = handle_registration(users_list[event.user_id])
                        users_list[event.user_id].set_id_msg_edit_anketa(message_id)
