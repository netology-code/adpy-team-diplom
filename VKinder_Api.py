from random import randrange
from datetime import date
import vk_api
from vk_api.longpoll import VkLongPoll
import re

with open('ApiKey.txt', 'r') as file_object:
    token = file_object.read().strip()

with open('TokenUser.txt', 'r') as file_object:
    token_user = file_object.read().strip()
vk_user = vk_api.VkApi(token=token_user)
session_api = vk_user.get_api()
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)



def get_user_token():
    pass


def get_photo(user_id):
    """
        Функция возвращает три последние аватарки в максимальном качестве.
    :param user_id: id пользователя
    """
    photo_info = session_api.photos.get(owner_id=user_id, album_id='profile', photo_sizes=True, extended=True,
                                        access_token=token_user)
    json_info = []
    for photo in photo_info['items'][-3:]:
        max_height = max(dict_h['height'] for dict_h in photo['sizes'])
        max_width = max(dict_w['width'] for dict_w in photo['sizes'])
        count_likes = str(photo['likes']['count'])
        for photo_max in photo['sizes']:
            if photo_max['height'] == max_height and photo_max['width'] == max_width:
                name_sizes = photo_max['type']
                link_photo = photo_max['url']
                info_photo = {
                    'size': name_sizes,
                    'count_likes': count_likes,
                    'url_photo': link_photo

                }
                for name_file in json_info:
                    if info_photo['file_name'] == name_file['file_name']:
                        info_photo['file_name'] = str(count_likes) + '_'
                json_info.append(info_photo)
                break
    return json_info


def write_msg(user_id, message, keyboard=None):
    vk.method('messages.send',
              {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), 'keyboard': keyboard})


def get_info(user_id):
    """
            Функция получается информацию о пользователе ФИ, город, пол и вычисляет возраст
    :param user_id: id пользователя
    """
    user_info = session_api.users.get(user_ids=(user_id), fields=('city', 'sex', 'bdate'))
    user_info = user_info[0]
    birthday = user_info['bdate']
    pattern_age = r'(\d+)\.(\d+)\.(\d{4})'
    if re.match(pattern_age, birthday):
        today = date.today()
        age = today.year - int(re.sub(pattern_age, r'\3', birthday)) - ((today.month, today.day) < (
        int(re.sub(pattern_age, r'\2', birthday)), int(re.sub(pattern_age, r'\1', birthday))))
    else:
        age = None
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
    """
        Функция производит поиск предложений на основе информации о пользователе и возвращает 5 предложений при дальнейшем поиске offset увеличивается на 5,
    Возвращает id предложения, ФИ, ссылку фото, возраст и ссылку на профиль
    :param name_city: Город
    :param age: Возраст
    :param gender: Пол
    :param offset: смещение поиска

    """
    users_info = session_api.users.search(hometown=name_city, sex=gender, status=6, age_from=age - 3, age_to=age + 3,
                                          count=5, offset=offset, fields=('photo_max_orig', 'bdate', 'city', 'sex'))
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

