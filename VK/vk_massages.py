from io import BytesIO

import requests
from vk_api import VkUpload
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from Repository.CardFind import CardFind
from User import User

edit_dict = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'age': 'Возраст',
            'gender': 'Пол',
            'city': 'город'
            }


def get_hello_massage(user_id, first_name):
    text_message = f'🚀 Привет, {first_name}!  👋  Я – бот, который экономит ' \
    f'твое время и помогает найти любовь быстро и легко! ' \
    f' ⏱️  Хочешь зарегистрироваться и начать поиск своей второй половинки?'

    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('хочу зарегистрироваться', color=VkKeyboardColor.POSITIVE)

    message = {
        'user_id': user_id,
        'message': text_message,
        'random_id': get_random_id(),
        'keyboard': keyboard.get_keyboard()
    }

    return message


def get_hello_massage_error(user_id):
    text_message = f'🚀 Привет! ' \
                   f'Извините, сервис не доступен.' \
                   f'Попробуйте отправить сообщение позже.'

    message = {
        'user_id': user_id,
        'message': text_message,
        'random_id': get_random_id()
    }

    return message


def get_registration_massage(user: User):
    text_message = f'Анкета:\n' \
                   f'новое значение - нажать кнопку\n'
    settings = dict(one_time=False, inline=True)
    keyboard = VkKeyboard(**settings)
    keyboard.add_button(label='Имя: '+user.get_first_name(), color=VkKeyboardColor.SECONDARY,
                                  payload={"action_edit_anketa": "first_name"})
    keyboard.add_line()
    keyboard.add_button(label='Фамилия: '+user.get_last_name(), color=VkKeyboardColor.SECONDARY,
                                   payload={"action_edit_anketa": "last_name"})
    keyboard.add_line()
    keyboard.add_button(label='Возраст: '+str(user.get_age()), color=VkKeyboardColor.SECONDARY,
                                   payload={"action_edit_anketa": "age"})
    keyboard.add_line()
    keyboard.add_button(label='Пол: '+str(user.get_gender_str()), color=VkKeyboardColor.SECONDARY,
                                   payload={"action_edit_anketa": "gender"})
    keyboard.add_line()
    keyboard.add_button(label='Город: '+user.get_city().get('title'), color=VkKeyboardColor.SECONDARY,
                                   payload={"action_edit_anketa": "city"})
    keyboard.add_line()
    keyboard.add_button(label='Сохранить анкету', color=VkKeyboardColor.POSITIVE,
                                   payload={"action_save_anketa": "save_anketa"})
    # keyboard.add_line()
    # keyboard.add_callback_button(label='Коротко обо мне: '+user.get_city().get('') + '\t', color=VkKeyboardColor.SECONDARY,
    #                                payload={"action": "edit_about_me"})

    message = {
        'user_id': user.get_user_id(),
        'message': text_message,
        'random_id': get_random_id(),
        'keyboard': keyboard.get_keyboard(),
        'peer_ids': user.get_user_id()
    }

    return message


def get_edit_massage(user_id, str_arg):
    text_message = f'Задайте новое значение ' + edit_dict[str_arg] + ':'
    if str_arg == 'gender':
        text_message += f'1 - Женщина, 2 - Мужчина'

    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Отмена', color=VkKeyboardColor.NEGATIVE,
                        payload={"action_cancel": "cancel_edit_anketa"})

    message = {
        'user_id': user_id,
        'message': text_message,
        'random_id': get_random_id(),
        'keyboard': keyboard.get_keyboard()
    }

    return message


def get_main_menu_massage(user: User):
    text_message = f'Главное меню'
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Поиск', color=VkKeyboardColor.PRIMARY,
                        payload={"action_main_manu": "find_users"})

    # keyboard.add_line()
    # keyboard.add_button('Критерии поиска', color=VkKeyboardColor.PRIMARY,
    #                     payload={"action_main_manu": "criteria"})


    keyboard.add_line()
    keyboard.add_button('Избранные', color=VkKeyboardColor.PRIMARY,
                        payload={"action_main_manu": "go_to_favorites"})

    # keyboard.add_line()
    # keyboard.add_button('В черный список', color=VkKeyboardColor.PRIMARY,
    #                     payload={"action_view": "go_to_exception"})

    # keyboard.add_button('Анкета', color=VkKeyboardColor.PRIMARY,
    #                     payload={"action_main_manu": "anketa"})
    message = {
        'user_id': user.get_user_id(),
        'message': text_message,
        'random_id': get_random_id(),
        'keyboard': keyboard.get_keyboard()
    }

    return message


def get_message_invitation(user_id):
    text_message = f'Для начала регистрации отправьте "start"'
    message = {
        'user_id': user_id,
        'message': text_message,
        'random_id': get_random_id()
    }
    return message


def get_message_done_registration(user_id):
    text_message = f'Регистрация закончена'
    message = {
        'user_id': user_id,
        'message': text_message,
        'random_id': get_random_id()
    }
    return message


def get_message_view(attachment, card, user: User):
    profile_str = 'https://vk.com/id' + str(card.id)
    text_message = f'{card.first_name} {card.last_name}\n' \
                   f'{profile_str}'

    keyboard = VkKeyboard(one_time=False)

    if user.get_index_view() > -1:
        if user.get_index_view() > 0:
            keyboard.add_button('Назад', color=VkKeyboardColor.PRIMARY,
                                payload={"action_view": "go_to_back"})

        if user.get_index_view() < user.get_size_list_cards()-1:
            keyboard.add_button('Вперед', color=VkKeyboardColor.PRIMARY,
                                payload={"action_view": "go_to_next"})

    if isinstance(card, CardFind):
        keyboard.add_line()
        keyboard.add_button('Добавить в избранные', color=VkKeyboardColor.PRIMARY,
                            payload={"action_view": "add_favorites"})
    else:
        if user.get_size_list_cards() > 1:
            keyboard.add_line()

        keyboard.add_button('Удалить из списка', color=VkKeyboardColor.PRIMARY,
                            payload={"action_view": "delete_from_list"})

    # keyboard.add_line()
    # keyboard.add_button('В черный список', color=VkKeyboardColor.PRIMARY,
    #                     payload={"action_view": "go_to_exception"})

    keyboard.add_line()
    keyboard.add_button('Главное меню', color=VkKeyboardColor.PRIMARY,
                        payload={"action_main_manu": "go_to_main_manu"})

    message = {
        'user_id': user.get_user_id(),
        'message': text_message,
        'attachment': attachment,
        'random_id': get_random_id(),
        'keyboard': keyboard.get_keyboard()
    }

    return message


def upload_photo(upload, url):
    img = requests.get(url).content
    f = BytesIO(img)

    response = upload.photo_messages(f)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']

    return {'owner_id': owner_id, 'photo_id': photo_id, 'access_key': access_key}


def get_message_error_search(user_id):
    text_message = f'По заданным параметрам\nничего найти не удалось'
    message = {
        'user_id': user_id,
        'message': text_message,
        'random_id': get_random_id()
    }
    return message


def get_message_criteria(user: User):
    text_message = f'Критерии поиска:\n' \
                   f'новое значение - нажать кнопку\n'
    criteria = user.get_criteria()
    settings = dict(one_time=False, inline=True)
    keyboard = VkKeyboard(**settings)
    keyboard.add_button(label='Пол: ' + "женщина" if criteria['gender_id'] == 1 else "мужчина", color=VkKeyboardColor.SECONDARY,
                        payload={"action_edit_criteria": "gender_id"})
    keyboard.add_line()
    keyboard.add_button(label='Статус: ' + "не женат (не замужем)" if criteria['status'] == 1 else "в активном поиске",
                        color=VkKeyboardColor.SECONDARY, payload={"action_edit_criteria": "status"})
    keyboard.add_line()
    keyboard.add_button(label='Возраст с: ' + str(criteria['age_from']), color=VkKeyboardColor.SECONDARY,
                        payload={"action_edit_criteria": "age_from"})
    keyboard.add_line()
    keyboard.add_button(label='Возраст по: ' + str(criteria['age_to']), color=VkKeyboardColor.SECONDARY,
                        payload={"action_edit_criteria": "age_to"})
    keyboard.add_line()
    keyboard.add_button(label='Город: ' + criteria['city_name'], color=VkKeyboardColor.SECONDARY,
                        payload={"action_edit_criteria": "city"})
    keyboard.add_line()
    keyboard.add_button(label='Есть фото' + "да" if criteria['has_photo'] == 1 else "нет", color=VkKeyboardColor.SECONDARY,
                        payload={"action_edit_criteria": "has_photo"})
    keyboard.add_line()
    keyboard.add_button(label='Сохранить критерии' + "да" if criteria['has_photo'] == 1 else "нет", color=VkKeyboardColor.POSITIVE,
                        payload={"action_edit_criteria": "save_criteria"})

    message = {
        'user_id': user.get_user_id(),
        'message': text_message,
        'random_id': get_random_id(),
        'keyboard': keyboard.get_keyboard(),
        'peer_ids': user.get_user_id()
    }

    return message