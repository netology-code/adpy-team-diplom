import re
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from configures import bot_token
from configures import database, user, password
from vk_users import get_user_info, search_possible_pair, get_photos
from db_manager import DBObject
from VKUser import VKUser


session = vk_api.VkApi(token=bot_token)

db_obj = DBObject(database, user, password)
db_obj.connect()
conn = db_obj.conn

users_to_be_shown = []
user_shown = None

def send_message(user_id, message, keyboard=None):
    post = {
        'user_id': user_id,
        'message': message,
        'random_id': 0
    }

    if keyboard is not None:
        post['keyboard'] = keyboard.get_keyboard()

    session.method('messages.send', post)


def send_attachments(user_id, attachment_list):
    post = {
        'user_id': user_id,
        'message': 'Фотографии:',
        'attachment': attachment_list,
        'random_id': 0
    }

    if keyboard is not None:
        post['keyboard'] = keyboard.get_keyboard()

    session.method('messages.send', post)

def check_str(pattern, user_str):
    res = re.match(pattern, user_str)
    return res is not None


def search_params(new_str):
    params = new_str.split(' ')
    if params[0] == 'женский':
        params[0] = 1
    elif params[0] == 'мужской':
        params[0] = 2
    return params


def show_one_user(user_id, users_to_be_shown) -> VKUser:
    if len(users_to_be_shown) > 0:
        actual_user = users_to_be_shown.pop(0)
        send_message(user_id, f'{actual_user.name} {actual_user.surname} {actual_user.url}')

        #<photo><user_id>_<photo_link>
        attachments = ''
        if len(actual_user.photos_dict) > 0:
            for photo_link, photo_like in actual_user.photos_dict.items():
                attachments += f'photo{actual_user.id}_{photo_link},'
            attachments = attachments[:-1]
            send_attachments(user_id, attachments)
        else:
            send_message(user_id, f'Closed profile. No photos available ')
        print(f'users left: {users_to_be_shown}')
        print(f'su actual: {actual_user}')
        return actual_user
    else:
        # request_new_users()
        print('request new users')


# пробная функция показа пользователей из избранного
def show_favorites_users(user_id):
    favorites = db_obj.show_favorites(conn, user_id)
    if not favorites:
        send_message(user_id, f"Sorry, but you haven't favorites")
    else:
        for item in favorites:
            send_message(user_id, f'{item.name} {item.surname} {item.url}')
    return favorites


# пробная функция по добавлению в черный список
def add_into_blacklist(user_id, own_id):
    possible_block = db_obj.check_if_in_blacklist(conn, user_id, own_id)
    if not possible_block:
        db_obj.add_user_to_blacklist(conn, own_id, user_id)
        send_message(user_id, f"User {own_id} was added into blacklist")
    else:
        send_message(user_id, f'Sorry, but this user already in blacklist')

    return possible_block


# пробная функция показа тех кто в чс
def show_black_list(user_id):
    black_list = db_obj.show_all_blacklist(conn, user_id)

    if not black_list:
        send_message(user_id, f"Your blacklist is clear")
    else:
        for item in black_list:
            send_message(user_id, f'{item.name} {item.surname} {item.url}')

    return black_list


for event in VkLongPoll(session).listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        text = event.text.lower()
        user_id = event.user_id

        # поиск информации пользователя бота
        user_info = get_user_info(user_id)

        keyboard = VkKeyboard(one_time=False)
        buttons = ['next', 'save', 'block', 'restart']
        buttons_colors = [VkKeyboardColor.SECONDARY, VkKeyboardColor.POSITIVE,
                          VkKeyboardColor.NEGATIVE, VkKeyboardColor.PRIMARY]
        for btn, btn_color in zip(buttons, buttons_colors):
            keyboard.add_button(btn, btn_color)

        if text == 'привет':
            send_message(user_id, 'Привет, для поиска пары введи: пол, возраст от и до, город', keyboard)
            send_message(user_id, 'Например: женский 25-30 Москва', keyboard)


            db_obj.add_user(db_obj. conn, user_info.id, user_info.name, user_info.surname, user_info.bdate,
                            user_info.gender, user_info.city, user_info.url)

            users_to_be_shown = []
            user_shown = None

        if check_str(r'[Аа-яЯ]{7}\s\d{2}-\d{2}\s[Аа-яЯ]+', text):
            new_params = search_params(text)
            peoples = search_possible_pair(new_params[0], new_params[1][:2],
                                           new_params[1][3:], new_params[2])

            first_photos = {}

            send_message(user_id, 'Подождите, идет загрузка результатов ...')

            for item in peoples:
                id_user = int(item.id)

                db_obj.add_possible_pair(db_obj.conn, user_id, id_user, item.name, item.surname, item.bdate, item.gender, item.city, item.url)

                photos_user = get_photos(id_user)

                if len(photos_user) > 0:
                    db_obj.add_user_photos(db_obj.conn, id_user, photos_user)

            users_to_be_shown = db_obj.get_users_info(db_obj.conn, user_id)
            user_shown = show_one_user(user_id, users_to_be_shown)

        elif text == 'next':
            user_shown = show_one_user(user_id, users_to_be_shown)

        elif text == 'save' and user_shown:
            db_obj.add_user_to_favourites(db_obj.conn, user_id, user_shown.id)

        elif text == 'block' and user_shown:
            db_obj.add_user_to_blacklist(db_obj.conn, user_id, user_shown.id)
        elif text == 'restart':
            print('restart')
            db_obj.disconnect()

# виджет ожидания, пока не загрузятся фото
# в фавориты в БД
# в черный список в БД

# запрос на следующих пользователей, старотовать с начала? как соотнести с БД
# убрать принты и возможные ошибки
