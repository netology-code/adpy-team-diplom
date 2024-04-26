import json

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
token = "vk1.a.BIz9EanDLhQLtuSTT5mVGSTvU7mIycKbGSzDDIVisPwVFO7VwFuglk4c8Z87XC1M0dS_fkkVsCll42WTCH5toPeEabcYTxCz6C7gqoLgTEKd6DrSD9uU0tofY8S3AhXZp_1Ln18-CKTWtrRn81IG18MBY2KAMrAIE3L_DuKKkNiW3sKzPQkdScH722rzshSP5asvFd_daoETjY_-2CzvSg"
authorize = vk_api.VkApi(token=token)
longpoll = VkLongPoll(authorize)
def get_user_response(vk_session, user_id, message):
    vk_session.method('messages.send', {
        'user_id': user_id,
        'message': message,
        'random_id': get_random_id()
    })
    for event in VkLongPoll(vk_session).listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            return event.text

# def get_user_photo(vk_session, user_id, message):
#     vk_session.method('messages.send', {
#         'user_id': user_id,
#         'message': message,
#         'random_id': get_random_id()
#     })
#     for event in VkLongPoll(vk_session).listen():
#         if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.attachments:
#             return event.attachments[0]['photo']['photo_130']

def create_user_profile(user_id, vk_session):
    user_info = {}
    questions = {

        "first_name": "Как тебя зовут?",
        "last_name": "Отлично! А какая у тебя фамилия?",
        "age": "Прекрасно! Сколько тебе лет?",
        "city": "Замечательный возраст , мы почти закончили! В каком городе ты живешь?",
        "about_me": "Прекрасно! Можешь кратко рассказать о своей жизни",
    }

    for key, question in questions.items():
        user_info[key] = get_user_response(vk_session, user_id, question) # Получаем ответы пользователя с помощью функции get_user_response

        # Запист в JSON-файл
    try:
        with open('questionnaires.json', 'r+') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

            print("Data before deletion:", data)  # Вывод data до удаления

            # Удаление предыдущей анкеты, если она существует
            if user_id in data:
                del data[user_id]
                print(f"Deleted profile for user {user_id}")
            else:
                print(f"No previous profile found for user {user_id}")

            print("Data after deletion:", data)  # Вывод data после удаления

            data[user_id] = user_info
            f.seek(0)
            json.dump(data, f, indent=4)

    except FileNotFoundError:  # Если JSON-файл не существует
        with open('questionnaires.json', 'w') as f:
            json.dump({user_id: user_info}, f, indent=4)

    print(f'Анкета пользователя {user_id} сохранена (предыдущая анкета удалена)!')
    print(f'Анкета пользователя {user_id}: {user_info}')
    for key, value in user_info.items():
        print(f'{key}: {value}')
