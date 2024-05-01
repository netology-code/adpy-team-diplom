import json
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv
import os
import VK.vk_massages as ms
from CheckBD.ABCCheckDb import ABCCheckDb
from CheckBD.CheckDBSQL import CheckDBSQL
from Repository.ABCRepository import ABCRepository
from Repository.SQLRepository import SQLRepository
from User import User
from VK.VKService import VKService

load_dotenv()

token = os.getenv(key='ACCESS_TOKEN')
token_api=os.getenv(key='ACCESS_TOKEN_API')
vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session)
users_list = {}
realization = os.getenv(key='REALIZATION')
repository: ABCRepository
сheckDB: ABCCheckDb


def handle_start(user_id):
    """
    Обработка начала работы, получение и заполнение данных из профися vk
    :param user_id: id пользователя
    :return:
    """
    if not user_id in users_list.keys():
        user = User(user_id)
        users_list[user_id] = user
        users_info = vk_srv.get_users_info(token=token_api, user_id=user.get_user_id())
        if not users_info is None:
            user.set_first_name(users_info['first_name'])
            user.set_last_name(users_info['last_name'])
            user.set_gender(users_info['sex'])
            if users_info.get('bdate'):
               user.set_age(vk_srv.determine_age(users_info['bdate']))
            user.set_city(users_info['city'])
            hello_message = ms.get_hello_massage(user.get_user_id(), user.get_first_name())
            send_message(hello_message)
        else:
            hello_massage_error = ms.get_hello_massage_error(user.get_user_id())
            send_message(hello_massage_error)
    else:
        # Уже есть в списке
        message_id = handle_registration(users_list[event.user_id])
        users_list[event.user_id].set_id_msg_edit_anketa(message_id)



def handle_registration(user: User):
    """
    Обработчмк нажатия кнопки "хочу зарегистрироваться"
    :param user: параметры пользователя
    :return: id сообщения при отправке
    """
    if user.get_id_msg_edit_anketa() > -1:
        vk_session.method('messages.delete', {'message_ids': user.get_id_msg_edit_anketa(), 'delete_for_all': 1})
    message_registration = ms.get_registration_massage(user)
    return send_message(message_registration)


def send_ask_edit(user: User, str_arg):
    """
    Отправка предложения заполнить значение анкеты
    и установка текущего шага для редактирования анкеты пользователя
    :param user: параметры пользователя
    :param str_arg: шаг
    """
    user.set_step(str_arg)
    message_edit = ms.get_edit_massage(user.get_user_id(), str_arg)
    send_message(message_edit)


def send_message(message):
    """
    Отправка сформированного сообщения
    :param message: сформированное сообщение
    """
    return vk_session.method('messages.send', message)


def set_param_anketa(user: User, text: str):
    """
    Запись текущего пункта анкеты в класс User
    :param user: параметры пользователя
    :param text: значение параметра
    """
    if user.get_step() == 'first_name':
        user.set_first_name(text)
    elif user.get_step() == 'last_name':
        user.set_last_name(text)
    elif user.get_step() == 'age':
        user.set_age(int(text))
    elif user.get_step() == 'age':
        user.set_age(int(text))
    elif user.get_step() == 'gender':
        user.set_gender(int(text))
    elif user.get_step() == 'city':
        city = vk_srv.get_city_by_name(token=token_api, text=text)
        user.set_city(city)


if __name__ == '__main__':
    if realization == 'SQL':
        сheckDB = CheckDBSQL()
        repository = SQLRepository()

    if сheckDB.check_db():
        vk_srv = VKService()
        for event in VkLongPoll(vk_session).listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                text = event.text.lower()

                # Начало работы
                if text == 'start':
                    handle_start(event.user_id)

                # Регистрация
                elif text == 'хочу зарегистрироваться':
                    message_id = handle_registration(users_list[event.user_id])
                    users_list[event.user_id].set_id_msg_edit_anketa(message_id)

                # Нажатие inline кнопок
                elif event.extra_values.get('payload'):

                    # Редактирование пунктов анкеты
                    if json.loads(event.extra_values.get('payload')).get('action_edit'):
                        str_arg = json.loads(event.extra_values.get('payload')).get('action_edit')
                        send_ask_edit(users_list[event.user_id], str_arg)

                    # Сохранить анкету
                    elif json.loads(event.extra_values.get('payload')).get('action_save'):
                        repository.add_user(users_list[event.user_id])
                        vk_session.method('messages.delete',
                                          dict(message_ids=users_list[event.user_id].get_id_msg_edit_anketa(),
                                               delete_for_all=1))
                        users_list[event.user_id].set_id_msg_edit_anketa(-1)

                    # Отмена текущего режима
                    elif json.loads(event.extra_values.get('payload')).get('action_cancel'):

                        # Отмена редактирования пункта анкеты
                        if json.loads(event.extra_values.get('payload')).get('action_cancel') == 'cancel_edit_anketa':
                            users_list[event.user_id].set_step(None)
                            message_id = handle_registration(users_list[event.user_id])
                            users_list[event.user_id].set_id_msg_edit_anketa(message_id)

                # Получение данных для текущего шага
                elif not users_list[event.user_id].get_step() is None:
                    set_param_anketa(users_list[event.user_id], text)
                    message_id = handle_registration(users_list[event.user_id])
                    users_list[event.user_id].set_id_msg_edit_anketa(message_id)
