from random import randrange
from datetime import date
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import re

with open('ApiKey.txt', 'r') as file_object:
    token = file_object.read().strip()

vk = vk_api.VkApi(token=token)
session_api = vk.get_api()
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})

# def get_user_token(user_id):
#     host = 'https://oauth.vk.com/authorize'
#     params = {
#         'client_id': user_id,
#         'redirect_uri': 'https://oauth.vk.com/blank.html',
#         'scope': 'friends'
#     }
#     data_users = requests.get(host, params=params).json()
#     print(data_users)
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
        'city': user_info['city']['title'],
        'gender': gender,
        'age': age
    }

    return user_info
def get_search(id_city, age, gender):
    with open('TokenUser.txt', 'r') as file_object:
        token_user = file_object.read().strip()
    vk = vk_api.VkApi(token=token_user)
    session_api = vk.get_api()
    users_info = session_api.users.search(city=id_city, sex=gender, status=6, age_from=age-3, age_to=age+3, limit=3, fields=('photo_max_orig', 'about'))
    profiles_list = []
    for user_info in users_info['items']:
        profile_info = {
            'first_name': user_info['first_name'],
            'last_name': user_info['last_name'],
            'photo_link': user_info['photo_max_orig'],
            'about': user_info['about'],
            'url_profile': 'https://vk.com/id' + str(user_info['id'])
        }
        profiles_list.append(profile_info)
    return profiles_list

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            if request == "привет":
                info_user = get_info(event.user_id)
                write_msg(event.user_id, f"Хай, {info_user['last_name']} {info_user['first_name']}, проживающий в городе {info_user['city']}")
                write_msg(event.user_id, f"Тебе {info_user['age']} лет")
                write_msg(event.user_id, f"Подыскать тебе пару?")
                gender_search = ('М', 'Ж').index(info_user['gender']) + 1
                result_list = get_search(832, info_user['age'], gender_search)
                for profile in result_list:
                    write_msg(event.user_id, f"{profile['first_name']} {profile['last_name']}\n"
                                             f"Фото: {profile['photo_link']}\n"
                                             f"Ссылка профиля: {profile['url_profile']}")
                    write_msg(event.user_id, f"Показать еще варианты?")
            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")
