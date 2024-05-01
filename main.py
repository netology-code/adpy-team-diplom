import json
from io import BytesIO

import requests
import vk_api
from vk_api import VkUpload
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


def save_anketa(user: User):
    repository.add_user(user)
    vk_session.method('messages.delete',
                      dict(message_ids=user.get_id_msg_edit_anketa(),
                           delete_for_all=1))
    user.set_id_msg_edit_anketa(-1)
    message_done_registration = ms.get_message_done_registration(user.get_user_id())
    send_message(message_done_registration)
    main_menu(user)


def main_menu(user: User):
    # Очистим данные о текущем списке просмотра
    user.set_list_cards(None)
    user.set_index_view(-1)
    user.set_id_msg_edit_anketa(-1)

    # Вывод главного меню
    message_main_menu = ms.get_main_menu_massage(user)
    send_message(message_main_menu)

def upload_photo(upload, url):
    img = requests.get(url).content
    f = BytesIO(img)

    response = upload.photo_messages(f)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return {'owner_id': owner_id, 'photo_id': photo_id, 'access_key': access_key}

def find_users(upload, vk_session, user: User):
    list_cards = vk_srv.users_search({}, token_api)
    if not list_cards is None:
        user.set_list_cards(list_cards)
        user.set_index_view(-1)


        view_next_card(upload, user)
    else:
        message_error_search = ms.get_message_error_search(user.get_user_id())
        send_message(message_error_search)


def view_next_card(upload, user):
    next_index = user.get_index_view()
    next_index = next_index + 1
    user.set_index_view(next_index)

    f = user.get_list_cards()[next_index]['photos'][0]

    photo1 = upload_photo(upload, f)
    attachment = f'photo{photo1["owner_id"]}_{photo1["photo_id"]}_{photo1["access_key"]}'
    message_view = ms.get_message_view(attachment, user.get_card(), user)
    send_message(message_view)


def view_back_card(user):
    next_index = user.get_index_view()
    next_index = next_index - 1
    user.set_index_view(next_index)
    message_view = ms.get_message_view(user.get_card(), user)
    send_message(message_view)
    # message = {
    #     'user_id': user.get_user_id(),
    #     'message': 'text_message',
    #     'random_id': 0
    # }
    # photos.getChatUploadServer
    # vk_session.method(ages.setChatPhoto(file: https://www.google.com/search?sca_esv=450a9a9b983914d8&sca_upv=1&rlz=1C1GCEA_ruRU1100RU1101&sxsrf=ACQVn0-U8-gKv1azUBVkyH2aRSHqRDal9Q:1714567650434&q=%D1%81%D0%BC%D0%B0%D0%B9%D0%BB%D0%B8%D0%BA%D0%B8&uds=AMwkrPs4mDHqV7QfY9nYaKRHgvE905tikM6txI8mkOUGPhWhJsLuF_nSnUEilZFtiWCJGUwJEKm32eQLmEJnqO9FFrS48qNYm20L9xIUbEr7ZwrQuZE5RZm_Ep3cWEnhGrhohgJnb-vL4JSpcpcq7dw3UM8qSdlOAvVuTN4WgrpvI6yDXiYBS1qBST6gT8lxPlr8r61ETtz0kvCC0vgRwkbm4vbdGpraZMgZsY3HspZFAqg9iepF8Ir1qD9sLSq3l3vD6jjAvo0BY8pzJl71JsMo8YWjCUoqVvUuqW6ygY9ek5iqkEXN7QZn34JqLAthztP0MWelYlRR&udm=2&prmd=ivsnmbt&sa=X&ved=2ahUKEwiFj_2dvuyFAxV0FxAIHawqBPYQtKgLegQIDRAB&biw=2560&bih=1313&dpr=1#vhid=MyYr974ugWAmnM&vssid=mosaic')


def check_user(user_id):
    user = repository.get_user(user_id)
    if user is None:
        message_invitation = ms.get_message_invitation(user_id)
        send_message(message_invitation)
    else:
        main_menu(user)

    return user

def open_criteria(user: User):
    user


if __name__ == '__main__':
    upload = VkUpload(vk_session)
    if realization == 'SQL':
        сheckDB = CheckDBSQL()
        repository = SQLRepository()

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
                    users_list[event.user_id].set_id_msg_edit_anketa(message_id)

                # Нажатие кнопок
                elif payload:
                    payload = json.loads(payload)
                    # Анкета
                    if payload.get('action_edit_anketa'):
                        str_arg = payload.get('action_edit')
                        send_ask_edit(users_list[event.user_id], str_arg)

                    # Сохранить анкету
                    elif payload.get('action_save_anketa'):
                        save_anketa(users_list[event.user_id])
                        open_criteria(users_list[event.user_id])

                    # Отмена текущего действия
                    elif payload.get('action_cancel'):
                        action = payload.get('action_main_manu')

                        # Отмена редактирования пункта анкеты
                        if action == 'cancel_edit_anketa':
                            users_list[event.user_id].set_step(None)
                            message_id = handle_registration(users_list[event.user_id])
                            users_list[event.user_id].set_id_msg_edit_anketa(message_id)

                    # Команды главного меню
                    elif payload.get('action_main_manu'):
                        action = payload.get('action_main_manu')

                        # Переход в главное меню
                        if action == 'go_to_main_manu':
                            main_menu(users_list[event.user_id])

                        # Поиск пользователей
                        elif action == 'find_users':
                            find_users(upload, vk_session, users_list[event.user_id])

                     # Просмотр текущего списка
                    elif payload.get('action_view'):
                        action = payload.get('action_view')
                        # Переход вперед
                        if action == 'go_to_next':
                            view_next_card(upload, users_list[event.user_id])

                        # Переход назад
                        elif action == 'go_to_back':
                            view_back_card(users_list[event.user_id])

                # Получение данных для текущего шага анкета или критерии поиска
                elif not users_list.get(event.user_id) is None and not users_list[event.user_id].get_step() is None:
                    set_param_anketa(users_list[event.user_id], text)
                    message_id = handle_registration(users_list[event.user_id])
                    users_list[event.user_id].set_id_msg_edit_anketa(message_id)

                # Просто сообщение от пользователя. Есть пользователь в базе или нет
                else:
                    if not event.user_id in users_list.keys():
                        users_list[event.user_id] = check_user(event.user_id)
