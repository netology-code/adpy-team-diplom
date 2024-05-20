import json
from io import BytesIO

import requests
import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv
import os
import VK.vk_messages as ms
from CheckBD.abc_check_db import ABCCheckDb
#from CheckBD.check_DBORM import CheckDBORM
from CheckBD.check_db_sql import CheckDBSQL
from Repository.abc_repository import ABCRepository
from Repository.card_exceptions import CardExceptions
from Repository.card_favorites import CardFavorites
#from Repository.ORMRepository import ORMRepository
from Repository.sql_repository import SQLRepository
from user import User
from VK.vk_service import VKService

import mechanics as mch

def handle_start(user_id):
    """
    Обработка начала работы, получение и заполнение данных из профися vk
    :param user_id: id пользователя
    :return:
    """
    if not user_id in mch.users_list.keys():
        user = User(user_id)
        mch.users_list[user_id] = user
        users_info = vk_srv.get_users_info(token=mch.token_api, user_id=user.get_user_id())
        if not users_info is None:
            user.set_first_name(users_info['first_name'])
            user.set_last_name(users_info['last_name'])
            user.set_gender(users_info['sex'])
            if users_info.get('bdate'):
               user.set_age(vk_srv.determine_age(users_info['bdate']))
            user.set_city({'id': users_info['city']['id'], 'name': users_info['city']['title']})
            hello_message = ms.get_hello_message(user.get_user_id(), user.get_first_name())
            send_message(hello_message)
        else:
            hello_message_error = ms.get_hello_mmessage_error(user.get_user_id())
            send_message(hello_message_error)
    else:
        # Уже есть в списке
        message_id = handle_registration(mch.users_list[event.user_id])
        mch.users_list[event.user_id].set_id_msg_edit_id(message_id)



def handle_registration(user: User):
    """
    Обработчмк нажатия кнопки "хочу зарегистрироваться"
    :param user: параметры пользователя
    :return: id сообщения при отправке
    """
    if user.get_id_msg_edit_id() > -1:
        mch.vk_session.method('messages.delete', {'message_ids': user.get_id_msg_edit_id(), 'delete_for_all': 1})
    message_registration = ms.get_registration_message(user)
    return send_message(message_registration)


def send_ask_edit_anketa(user: User, str_arg):
    """
    Отправка предложения заполнить значение анкеты
    и установка текущего шага для редактирования анкеты пользователя
    :param user: параметры пользователя
    :param str_arg: шаг
    """
    user.set_step('anketa_'+str_arg)
    message_edit = ms.get_edit_message(user.get_user_id(), str_arg)
    send_message(message_edit)


def send_message(message):
    """
    Отправка сформированного сообщения
    :param message: сформированное сообщение
    """
    return mch.vk_session.method('messages.send', message)



if __name__ == '__main__':
    upload = VkUpload(mch.vk_session)
    if mch.realization == 'SQL':
        сheckDB = CheckDBSQL()
        repository = SQLRepository()
    # else:
    #     сheckDB = CheckDBORM()
    #     repository = ORMRepository()


    if сheckDB.check_db():
        vk_srv = VKService()
        for event in VkLongPoll(mch.vk_session).listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                text = event.text.lower()
                payload = event.extra_values.get('payload')

                # Начало работы
                if text == 'start':
                    handle_start(event.user_id)

                # Регистрация
                elif text == 'хочу зарегистрироваться':
                    message_id = handle_registration(mch.users_list[event.user_id])
                    mch.users_list[event.user_id].set_id_msg_edit_id(message_id)

                # Нажатие кнопок
                elif payload:
                    payload = json.loads(payload)
                    # Анкета
                    if payload.get('action_edit_anketa'):
                        str_arg = payload.get('action_edit_anketa')
                        send_ask_edit_anketa(mch.users_list[event.user_id], str_arg)

                    # Критерии поиска
                    elif payload.get('action_edit_criteria'):
                        str_arg = payload.get('action_edit_criteria')
                        mch.send_ask_edit_criteria(mch.users_list[event.user_id], str_arg)

                    # Сохранить критерии
                    elif payload.get('action_save_criteria'):
                        mch.save_criteria(mch.users_list[event.user_id])

                    # Сохранить анкету
                    elif payload.get('action_save_anketa'):
                        mch.save_anketa(mch.users_list[event.user_id])
                        message_id = mch.handle_criteria(mch.users_list[event.user_id])
                        mch.users_list[event.user_id].set_id_msg_edit_id(message_id)

                    # Отмена текущего действия
                    elif payload.get('action_cancel'):
                        action = payload.get('action_cancel')

                        # Отмена редактирования пункта анкеты
                        if action == 'cancel_edit_anketa':
                            mch.users_list[event.user_id].set_step(None)
                            message_id = handle_registration(mch.users_list[event.user_id])
                            mch.users_list[event.user_id].set_id_msg_edit_id(message_id)


                    # Команды главного меню
                    elif payload.get('action_main_manu'):
                        action = payload.get('action_main_manu')

                        # Переход в главное меню
                        if action == 'go_to_main_manu':
                            mch.main_menu(mch.users_list[event.user_id])

                        # Поиск пользователей
                        elif action == 'find_users':
                            mch.find_users(upload, mch.users_list[event.user_id], vk_srv, mch.token_api)

                        # Открыть список избранных
                        elif action == 'go_to_favorites':
                            mch.go_to_favorites(upload, mch.users_list[event.user_id], repository, mch.token_api)

                        # Редактировать критерии поиска
                        elif action == 'criteria':
                            message_id = mch.handle_criteria(mch.users_list[event.user_id])
                            mch.users_list[event.user_id].set_id_msg_edit_id(message_id)

                     # Просмотр текущего списка
                    elif payload.get('action_view'):
                        action = payload.get('action_view')
                        # Переход вперед
                        if action == 'go_to_next':
                            mch.view_next_card(upload, mch.users_list[event.user_id], vk_srv, mch.token_api)

                        # Переход назад
                        elif action == 'go_to_back':
                            mch.view_back_card(mch.users_list[event.user_id])

                        # Переход назад
                        elif action == 'add_favorites':
                            mch.add_favorites(repository, mch.users_list[event.user_id])

                        # Открыть список избранных
                        elif action == 'delete_from_list':
                            mch.delete_from_list(mch.users_list[event.user_id], repository)

                # Получение данных для текущего шага анкета или критерии поиска
                elif not mch.users_list.get(event.user_id) is None and not mch.users_list[event.user_id].get_step() is None:
                    mch.set_param(mch.users_list[event.user_id], text)
                    if 'anketa' in mch.users_list[event.user_id].get_step():
                        message_id = handle_registration(mch.users_list[event.user_id])
                        mch.users_list[event.user_id].set_id_msg_edit_id(message_id)
                    else:
                        message_id = mch.handle_criteria(mch.users_list[event.user_id])
                        mch.users_list[event.user_id].set_id_msg_edit_id(message_id)

                # Просто сообщение от пользователя. Есть пользователь в базе или нет
                else:
                    if not event.user_id in mch.users_list.keys():
                        user = mch.check_user(event.user_id)
                        if user:
                            mch.users_list[event.user_id] = user
