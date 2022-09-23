import re
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from configures import bot_token
from vk_users import get_user_info, search_possible_pair, get_photos


session = vk_api.VkApi(token=bot_token)


def send_message(user_id, message, keyboard=None):
    post = {
        'user_id': user_id,
        'message': message,
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


for event in VkLongPoll(session).listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        text = event.text.lower()
        user_id = event.user_id

        keyboard = VkKeyboard(one_time=False)
        buttons = ['next', 'save', 'block', 'write']
        buttons_colors = [VkKeyboardColor.SECONDARY, VkKeyboardColor.POSITIVE,
                          VkKeyboardColor.NEGATIVE, VkKeyboardColor.PRIMARY]
        for btn, btn_color in zip(buttons, buttons_colors):
            keyboard.add_button(btn, btn_color)

        if text == 'привет':
            send_message(user_id, 'Привет, для поиска пары введи: пол, возраст от и до, город', keyboard)
            send_message(user_id, 'Например: женский 25-30 Москва', keyboard)

        if check_str(r'[Аа-яЯ]{7}\s\d{2}-\d{2}\s[Аа-яЯ]+', text):
            new_params = search_params(text)

            peoples = search_possible_pair(new_params[0], new_params[1][:2],
                                           new_params[1][3:], new_params[2])

            for item in peoples:
                id_user = int(item[-1])
                photos_user = get_photos(id_user)
                send_message(user_id, f'{str(item[0])} {item[1]} {item[2]}')
                for photo in photos_user:
                    send_message(user_id, f'{str(photo[1])}')

# bot работает, все присылает, но вылетает исключение если профиль закрыт, добавлю try exept но уже завтра
