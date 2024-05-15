from io import BytesIO
from main import event, message_id
import requests
import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll
from dotenv import load_dotenv
import os
import VK.vk_messages as ms
from CheckBD.ABCCheckDb import ABCCheckDb
from Repository.ABCRepository import ABCRepository
from Repository.CardExceptions import CardExceptions
from Repository.CardFavorites import CardFavorites

from User import User

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
from main import vk_srv, send_message


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
    img = requests.get(url).content
    f = BytesIO(img)

    response = upload.photo_messages(f)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return {'owner_id': owner_id, 'photo_id': photo_id, 'access_key': access_key}


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


def go_to_favorites(upload, user: User, repository, token_api):
    list_cards = repository.get_favorites(user.get_user_id(), token_api)
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