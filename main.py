from random import randrange
from datetime import date
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from VKinder_DB import *
import re


with open('ApiKey.txt', 'r') as file_object:
    token = file_object.read().strip()

vk = vk_api.VkApi(token=token)
session_api = vk.get_api()
longpoll = VkLongPoll(vk)

keyboard = VkKeyboard(one_time=True)
keyboard.add_button('Давай!', color=VkKeyboardColor.POSITIVE)
keyboard.add_button('Нет спасибо!', color=VkKeyboardColor.NEGATIVE)

keyboard_restart = VkKeyboard(one_time=True)
keyboard_restart.add_button('Покажи еще!', color=VkKeyboardColor.POSITIVE)
keyboard_restart.add_button('Хватит!', color=VkKeyboardColor.NEGATIVE)

keyboard_continue = VkKeyboard(one_time=False)
keyboard_continue.add_button('Дальше!', color=VkKeyboardColor.POSITIVE)
keyboard_continue.add_button('В избранное!', color=VkKeyboardColor.PRIMARY)
keyboard_continue.add_button('В черный список!', color=VkKeyboardColor.SECONDARY)
keyboard_continue.add_button('Остановись!', color=VkKeyboardColor.NEGATIVE)


def write_msg(user_id, message, keyboard=None):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7), 'keyboard': keyboard})

def get_info(user_id):
    user_info = session_api.users.get(user_ids=(user_id), fields=('city', 'sex', 'bdate'))
    user_info = user_info[0]
    birthday = user_info['bdate']
    pattern_age = r'(\d+)\.(\d+)\.(\d{4})'
    if re.match(pattern_age, birthday):
        today = date.today()
        age = today.year - int(re.sub(pattern_age, r'\3', birthday)) - ((today.month, today.day) < (int(re.sub(pattern_age, r'\2', birthday)), int(re.sub(pattern_age, r'\1', birthday))))
    else:
        age = 'Одному богу известно сколько'
    gender = ('-', 'Ж', 'М')[user_info['sex']]

    user_info = {
        'first_name': user_info['first_name'],
        'last_name': user_info['last_name'],
        'city': user_info['city'],
        'gender': gender,
        'age': age
    }

    return user_info

def get_search(name_city, age, gender, offset=0):
    with open('TokenUser.txt', 'r') as file_object:
        token_user = file_object.read().strip()
    vk = vk_api.VkApi(token=token_user)
    session_api = vk.get_api()
    users_info = session_api.users.search(hometown=name_city, sex=gender, status=6, age_from=age - 3, age_to=age + 3, count=5, offset=offset, fields=('photo_max_orig', 'bdate', 'city', 'sex'))
    profiles_list = []
    for user_info in users_info['items']:
        if user_info["is_closed"]:
            continue
        birthday = user_info['bdate']
        pattern_age = r'(\d+)\.(\d+)\.(\d{4})'
        today = date.today()
        age = today.year - int(re.sub(pattern_age, r'\3', birthday)) - ((today.month, today.day) < (
        int(re.sub(pattern_age, r'\2', birthday)), int(re.sub(pattern_age, r'\1', birthday))))
        gender = ('-', 'Ж', 'М')[user_info['sex']]
        id_offer = str(user_info['id'])
        profile_info = {
            'id_offer': id_offer,
            'first_name': user_info['first_name'],
            'last_name': user_info['last_name'],
            'photo_link': user_info['photo_max_orig'],
            'city': user_info['city'],
            'gender': gender,
            'agе': age,
            'url_profile': 'https://vk.com/id' + id_offer
        }
        profiles_list.append(profile_info)
    return profiles_list


for event in longpoll.listen():
    info_user = get_info(event.user_id)
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            # add_user(event.user_id, info_user['first_name'], info_user['gender'], info_user['age'], info_user['city']['title'])
            if request == "привет":
                write_msg(event.user_id, f"Хай, {info_user['last_name']} {info_user['first_name']}, проживающий  в городе {info_user['city']['title']}")
                write_msg(event.user_id, f"Тебе {info_user['age']} лет")
                write_msg(event.user_id, f"Подыскать тебе пару?", keyboard.get_keyboard())
                gender_search = ('М', 'Ж').index(info_user['gender']) + 1
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                            request = event.text
                            if request == "Давай!":
                                offset = 0
                                stoped = False
                                result_list = get_search(info_user['city']['id'], info_user['age'], gender_search, offset)
                                for profile in result_list:
                                    if stoped:
                                        break
                                    # add_offer(event.user_id, profile['id_offer'], profile['first_name'], profile['last_name'], profile['gender'], profile['agе'], profile['city']['title'])
                                    write_msg(event.user_id, f"{profile['first_name']} {profile['last_name']} {profile['agе']} лет.\n"
                                                             f"Фото: {profile['photo_link']}\n"
                                                             f"Ссылка профиля: {profile['url_profile']}")
                                    write_msg(event.user_id, f"Показать еще варианты?", keyboard_continue.get_keyboard())
                                    for event in longpoll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW:
                                            if event.to_me:
                                                request = event.text
                                                if request == "Дальше!":
                                                    break
                                                elif request == "Остановись!":
                                                    stoped = True
                                                    break
                                                elif request == "В избранное!":
                                                    add_favorite(event.user_id, profile['id_offer'])
                                                    write_msg(event.user_id, f"Я добавил {profile['first_name']} в ваш список избранного!")
                                                    break
                                                elif request == "В черный список!":
                                                    add_black_list(event.user_id, profile['id_offer'])
                                                    write_msg(event.user_id, f"Я больше не буду показывать вам профиль {profile['first_name']} !")
                                                    break
                                write_msg(event.user_id, "У меня на этом все!", keyboard_restart.get_keyboard())
                                break
                            elif request == "Нет спасибо!":
                                break
            elif request == "Покажи еще!":
                offset += 5
                stoped = False
                result_list = get_search(info_user['city']['title'], info_user['age'], gender_search, offset)
                for profile in result_list:
                    if stoped:
                        break
                    write_msg(event.user_id, f"{profile['first_name']} {profile['last_name']} {profile['agе']} лет.\n"
                                             f"Фото: {profile['photo_link']}\n"
                                             f"Ссылка профиля: {profile['url_profile']}")
                    write_msg(event.user_id, f"Показать еще варианты?", keyboard_continue.get_keyboard())
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW:
                            if event.to_me:
                                request = event.text
                                if request == "Дальше!":
                                    break
                                elif request == "Остановись!":
                                    stoped = True
                                    break
                                elif request == "В избранное!":
                                    write_msg(event.user_id,
                                              f"Я добавил {profile['first_name']} в ваш список избранного!")
                                    break
                                elif request == "В черный список!":
                                    write_msg(event.user_id,
                                              f"Я больше не буду показывать вам профиль {profile['first_name']} !")
                                    break
                write_msg(event.user_id, "У меня на этом все!", keyboard_restart.get_keyboard())
            elif request == "Хватит!" or request == "Нет спасибо!":
                write_msg(event.user_id, "Ноу проблем...")
            else:
                write_msg(event.user_id, "Не понял вашего ответа...")
