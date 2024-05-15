import json
from enum import Enum
from io import BytesIO

import requests
import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv
import os
import VK.vk_messages as ms
from CheckBD.ABCCheckDb import ABCCheckDb
from CheckBD.CheckDBORM import CheckDBORM
from CheckBD.CheckDBSQL import CheckDBSQL
from Repository.ABCRepository import ABCRepository
from Repository.CardExceptions import CardExceptions
from Repository.CardFavorites import CardFavorites
from Repository.ORMRepository import ORMRepository
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
class TyleRealization(Enum):
    sql = 'SQL'
    orm = 'ORM'
repository: ABCRepository
сheckDB: ABCCheckDb
upload:VkUpload


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
            user.set_city({'id': users_info['city']['id'], 'name': users_info['city']['title']})
            hello_message = ms.get_hello_message(user.get_user_id(), user.get_first_name())
            send_message(hello_message)
        else:
            hello_message_error = ms.get_hello_mmessage_error(user.get_user_id())
            send_message(hello_message_error)
    else:
        # Уже есть в списке
        message_id = handle_registration(users_list[event.user_id])
        users_list[event.user_id].set_id_msg_edit_id(message_id)



def handle_registration(user: User):
    """
    Обработчмк нажатия кнопки "хочу зарегистрироваться"
    :param user: параметры пользователя
    :return: id сообщения при отправке
    """
    if user.get_id_msg_edit_id() > -1:
        vk_session.method('messages.delete', {'message_ids': user.get_id_msg_edit_id(), 'delete_for_all': 1})
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
    return vk_session.method('messages.send', message)


def set_param(user: User, text: str):
    """
    Запись текущего пункта анкеты в класс User
    :param user: параметры пользователя
    :param text: значение параметра
    """
    if user.get_step() == 'anketa_first_name':
        user.set_first_name(text)
    elif user.get_step() == 'anketa_last_name':
        user.set_last_name(text)
    elif user.get_step() == 'anketa_age':
        user.set_age(text)
    elif user.get_step() == 'anketa_gender':
        user.set_gender(int(text))
    elif user.get_step() == 'anketa_city':
        city = vk_srv.get_city_by_name(token=token_api, text=text)
        user.set_city(city)
    else:
        if user.get_step() == 'criteria_gender':
            user.get_criteria().gender_id = int(text)
        elif user.get_step() == 'criteria_age':
            age = text.split('-')
            user.get_criteria().age_from = age[0]
            user.get_criteria().age_to = age[1]
        elif user.get_step() == 'criteria_status':
            user.get_criteria().status = int(text)
        elif user.get_step() == 'criteria_has_photo':
            user.get_criteria().has_photo = int(text)
        elif user.get_step() == 'criteria_city':
            city = vk_srv.get_city_by_name(token=token_api, text=text)
            user.get_criteria().city = city


def save_anketa(user: User):
    repository.add_user(user)
    vk_session.method('messages.delete',
                      dict(message_ids=user.get_id_msg_edit_id(),
                           delete_for_all=1))
    user.set_id_msg_edit_id(-1)
    # message_done_registration = ms.get_message_done_registration(user.get_user_id())
    # send_message(message_done_registration)
    #main_menu(user)


def main_menu(user: User):
    # Очистим данные о текущем списке просмотра
    user.set_list_cards(None)
    user.set_index_view(-1)
    user.set_id_msg_edit_id(-1)

    # Вывод главного меню
    message_main_menu = ms.get_main_menu_message(user)
    send_message(message_main_menu)


def upload_photo(upload, url):

    if url:
        img = requests.get(str(url)).content
        f = BytesIO(img)

        response = upload.photo_messages(f)[0]

        owner_id = response['owner_id']
        photo_id = response['id']
        access_key = response['access_key']

        return {'owner_id': owner_id, 'photo_id': photo_id, 'access_key': access_key}

    else:
        return {}

def find_users(upload, user: User, vk_srv, token):
    list_cards = vk_srv.users_search(user.get_criteria(), token_api)
    if not list_cards is None:
        user.set_list_cards(list_cards)
        user.set_index_view(-1)
        view_next_card(upload, user, vk_srv, token)
    else:
        message_error_search = ms.get_message_error_search(user.get_user_id())
        send_message(message_error_search)


def view_next_card(upload, user: User, vk_srv, token):
    if user.get_size_list_cards() > 0:
        next_index = user.get_index_view()
        next_index = next_index + 1
        if next_index == user.get_size_list_cards():
            next_index = next_index - 1
        user.set_index_view(next_index)

        photos = user.get_list_cards()[next_index].photos
        attachment = []
        for photo in photos:
            photo_struct = upload_photo(upload, photo)
            if photo_struct:
                attachment.append(f'photo{photo_struct["owner_id"]}_{photo_struct["photo_id"]}_{photo_struct["access_key"]}')

        message_view = ms.get_message_view(','.join(attachment), user.get_card(), user)
        send_message(message_view)
        if user.get_size_list_cards()-1 > next_index and not user.get_list_cards()[next_index+1].photos:
            vk_srv.add_photos(user.get_list_cards()[next_index+1], token)
    else:
        main_menu(user)


def view_back_card(user):
    next_index = user.get_index_view()
    next_index = next_index - 1
    user.set_index_view(next_index)

    photos = user.get_list_cards()[next_index].photos
    attachment = []
    for photo in photos:
        photo_struct = upload_photo(upload, photo)
        if photo_struct:
            attachment.append(f'photo{photo_struct["owner_id"]}_{photo_struct["photo_id"]}_{photo_struct["access_key"]}')

    message_view = ms.get_message_view(','.join(attachment), user.get_card(), user)
    send_message(message_view)


def check_user(user_id):
    user = repository.get_user(user_id)
    if user is None:
        message_invitation = ms.get_message_invitation(user_id)
        send_message(message_invitation)
    else:
        main_menu(user)

    return user


def handle_criteria(user: User):
    if user.get_criteria() is None:
        criteria_dict = repository.open_criteria(user.get_user_id())
        user.set_criteria(criteria_dict)
    message_criteria = ms.get_message_criteria(user)
    if user.get_id_msg_edit_id() > -1:
        vk_session.method('messages.delete', {'message_ids': user.get_id_msg_edit_id(), 'delete_for_all': 1})
    return send_message(message_criteria)


def send_ask_edit_criteria(user, str_arg):
    user.set_step('criteria_'+str_arg)
    message_edit = ms.get_edit_message(user.get_user_id(), str_arg)
    send_message(message_edit)


def add_favorites(repository, user: User):
    repository.add_favorites(user)


def go_to_favorites(upload, user: User, repository):
    list_cards = repository.get_favorites(user.get_user_id())
    if not list_cards is None:
        user.set_list_cards(list_cards)
        user.set_index_view(-1)
        view_next_card(upload, user, vk_srv, token)
    else:
        message_error_search = ms.get_message_error_search(user.get_user_id())
        send_message(message_error_search)


def delete_from_list(user: User, repository):
    if len(user.get_list_cards()) > 0:
        if isinstance(user.get_list_cards()[0], CardFavorites):
            repository.delete_favorites(user.get_user_id(), user.get_card().profile)
        elif isinstance(user.get_list_cards()[0], CardExceptions):
            repository.delete_exceptions(user.get_user_id(), user.get_card().profile)

    user.delete_card()
    view_next_card(upload, user, vk_srv, token)


def save_criteria(user: User):
    repository.save_criteria(user)
    users_list[event.user_id].set_id_msg_edit_id(message_id)
    vk_session.method('messages.delete',
                      dict(message_ids=user.get_id_msg_edit_id(),
                           delete_for_all=1))
    message_done_registration = ms.get_message_done_registration(user.get_user_id())
    send_message(message_done_registration)
    main_menu(user)


def go_to_exceptions(upload, user: User, repository):
    list_cards = repository.get_exceptions(user.get_user_id())
    if not list_cards is None:
        user.set_list_cards(list_cards)
        user.set_index_view(-1)
        view_next_card(upload, user, vk_srv, token)
    else:
        message_error_search = ms.get_message_error_search(user.get_user_id())
        send_message(message_error_search)


def add_exceptions(repository, user: User):
    repository.add_exceptions(user)


if __name__ == '__main__':
    upload = VkUpload(vk_session)

    if realization == 'SQL':
        сheckDB = CheckDBSQL()
        repository = SQLRepository()

    elif realization == 'ORM':
        сheckDB = CheckDBORM()
        repository = ORMRepository()

    if сheckDB.check_db():
        vk_srv = VKService()
        for event in VkLongPoll(vk_session).listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                text = event.text.lower()
                payload = event.extra_values.get('payload')

                # Начало работы
                if text == 'start':
                    handle_start(event.user_id)

                # Регистрация
                elif text == 'хочу зарегистрироваться':
                    message_id = handle_registration(users_list[event.user_id])
                    users_list[event.user_id].set_id_msg_edit_id(message_id)

                # Нажатие кнопок
                elif payload:
                    payload = json.loads(payload)
                    # Анкета
                    if payload.get('action_edit_anketa'):
                        str_arg = payload.get('action_edit_anketa')
                        send_ask_edit_anketa(users_list[event.user_id], str_arg)

                    # Критерии поиска
                    elif payload.get('action_edit_criteria'):
                        str_arg = payload.get('action_edit_criteria')
                        send_ask_edit_criteria(users_list[event.user_id], str_arg)

                    # Сохранить критерии
                    elif payload.get('action_save_criteria'):
                        save_criteria(users_list[event.user_id])

                    # Сохранить анкету
                    elif payload.get('action_save_anketa'):
                        save_anketa(users_list[event.user_id])
                        message_id = handle_criteria(users_list[event.user_id])
                        users_list[event.user_id].set_id_msg_edit_id(message_id)

                    # Отмена текущего действия
                    elif payload.get('action_cancel'):
                        action = payload.get('action_cancel')

                        # Отмена редактирования пункта анкеты
                        if action == 'cancel_edit_anketa':
                            users_list[event.user_id].set_step(None)
                            message_id = handle_registration(users_list[event.user_id])
                            users_list[event.user_id].set_id_msg_edit_id(message_id)


                    # Команды главного меню
                    elif payload.get('action_main_manu'):
                        action = payload.get('action_main_manu')

                        # Переход в главное меню
                        if action == 'go_to_main_manu':
                            main_menu(users_list[event.user_id])

                        # Поиск пользователей
                        elif action == 'find_users':
                            find_users(upload, users_list[event.user_id], vk_srv, token_api)

                        # Открыть список избранных
                        elif action == 'go_to_favorites':
                            go_to_favorites(upload, users_list[event.user_id], repository)

                        # Открыть черный избранных
                        elif action == 'go_to_exception':
                            go_to_exceptions(upload, users_list[event.user_id], repository)

                        # Редактировать критерии поиска
                        elif action == 'criteria':
                            message_id = handle_criteria(users_list[event.user_id])
                            users_list[event.user_id].set_id_msg_edit_id(message_id)

                     # Просмотр текущего списка
                    elif payload.get('action_view'):
                        action = payload.get('action_view')
                        # Переход вперед
                        if action == 'go_to_next':
                            view_next_card(upload, users_list[event.user_id], vk_srv, token_api)

                        # Переход назад
                        elif action == 'go_to_back':
                            view_back_card(users_list[event.user_id])

                        # Добавить в избранное
                        elif action == 'add_favorites':
                            add_favorites(repository, users_list[event.user_id])

                        # Добавить в избранное
                        elif action == 'add_favorites':
                            add_favorites(repository, users_list[event.user_id])

                        # Удалить из избранных
                        elif action == 'delete_from_list':
                            delete_from_list(users_list[event.user_id], repository)

                        # Добавить в черный список
                        elif action == 'add_exceptions':
                            add_exceptions(repository, users_list[event.user_id])

                # Получение данных для текущего шага анкета или критерии поиска
                elif not users_list.get(event.user_id) is None and not users_list[event.user_id].get_step() is None:
                    set_param(users_list[event.user_id], text)
                    if 'anketa' in users_list[event.user_id].get_step():
                        message_id = handle_registration(users_list[event.user_id])
                        users_list[event.user_id].set_id_msg_edit_id(message_id)
                    else:
                        message_id = handle_criteria(users_list[event.user_id])
                        users_list[event.user_id].set_id_msg_edit_id(message_id)

                # Просто сообщение от пользователя. Есть пользователь в базе или нет
                else:
                    if not event.user_id in users_list.keys():
                        user = check_user(event.user_id)
                        if user:
                            users_list[event.user_id] = user
