import json
import vk_api
from configures import token_vk, bot_token
from VKUser import VKUser


def get_user_info(user_id):
    vk = vk_api.VkApi(token=bot_token)
    response = vk.method('users.get', {'user_ids': user_id, 'fields': 'bdate, sex, city, relation'})

    if 'city' in response[0]:
        city = response[0]['city']['title']
    else:
        city = 'Город не указан'

    if 'bdate' in response[0]:
        bdate = response[0]['bdate']

    else:
        bdate = 'не указан возраст'

    info = VKUser(response[0]['id'], response[0]['first_name'], response[0]['last_name'], bdate,
                  response[0]['sex'], city)
    info.url = f"https://vk.com/id{response[0]['id']}"

    return info


def search_possible_pair(sex, age_from, age_to, city):
    possible_list = []
    vk = vk_api.VkApi(token=token_vk)
    response = vk.method('users.search', {'sex': sex, 'status': 6, 'age_from': age_from,
                                          'age_to': age_to, 'has_photo': 1,
                                          'count': 100, 'online': 0, 'hometown': city})

    for item in response['items']:
        vk_user = get_user_info(item['id'])
        possible_list.append(vk_user)

    return possible_list


def get_photos(person_id):
    vk = vk_api.VkApi(token=token_vk)
    try:
        response = vk.method('photos.get', {'owner_id': person_id, 'album_id': 'profile',
                                            'extended': 1,
                                            'photo_sizes': 1})
    except vk_api.exceptions.ApiError:
        print('Closed profile')
        return {}

    print(response)

    users_photos = []
    user_photos_dict = {}

    for item in range(len(response['items'])):
        users_photos.append([response['items'][item]['likes']['count'],
                             response['items'][item]['id']])

    photos = sorted(users_photos, key=lambda x: int(x[0]), reverse=True)
    photos_three = photos[:3] if len(photos) >= 3 else photos
    print(photos_three)
    for photo in photos_three:
        user_photos_dict[photo[1]] = photo[0]

    return user_photos_dict
