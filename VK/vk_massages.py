from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

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
                                  payload={"action_edit": "first_name"})
    keyboard.add_line()
    keyboard.add_button(label='Фамилия: '+user.get_last_name(), color=VkKeyboardColor.SECONDARY,
                                   payload={"action_edit": "last_name"})
    keyboard.add_line()
    keyboard.add_button(label='Возраст: '+str(user.get_age()), color=VkKeyboardColor.SECONDARY,
                                   payload={"action_edit": "age"})
    keyboard.add_line()
    keyboard.add_button(label='Пол: '+str(user.get_gender_str()), color=VkKeyboardColor.SECONDARY,
                                   payload={"action_edit": "gender"})
    keyboard.add_line()
    keyboard.add_button(label='Город: '+user.get_city().get('title'), color=VkKeyboardColor.SECONDARY,
                                   payload={"action_edit": "city"})
    keyboard.add_line()
    keyboard.add_button(label='Сохранить анкету', color=VkKeyboardColor.POSITIVE,
                                   payload={"action_save": "save_anketa"})
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
