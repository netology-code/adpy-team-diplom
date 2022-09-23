import requests
import vk_api
from configures import token_vk, bot_token

#получаем инфу о пользователе
def get_user_info(user_id):
    vk = vk_api.VkApi(token=bot_token)
    response = vk.method('users.get', {'user_ids': user_id, 'fields': 'bdate, sex, city'})
    info = [response[0]['id'], response[0]['first_name'], response[0]['last_name'],
            response[0]['sex'], response[0]['city']['title'],
            f"https://vk.com/id{response[0]['id']}"]

    return info

#ищем пару по указанным параметрам, подумал что будет удобно если человек будет сам выбирать, возраст, город, пол
def search_possible_pair(sex, age_from, age_to, city):
    possible_list = []
    vk = vk_api.VkApi(token=token_vk)
    response = vk.method('users.search', {'sex': sex, 'status': 6, 'age_from': age_from,
                                          'age_to': age_to, 'has_photo': 1,
                                          'count': 10, 'online': 0, 'hometown': city})

    for item in response['items']:
        new_list = [item['first_name'], item['last_name'], f"https://vk.com/id{str(item['id'])}",
                    item['id']]
        possible_list.append(new_list)
    return possible_list

#получим отсортированные фото того кто понравится пользователю
def get_photos(person_id):
    vk = vk_api.VkApi(token=token_vk)
    response = vk.method('photos.get', {'owner_id': person_id, 'album_id': 'profile',
                                        'count': 5, 'extended': 1,
                                        'photo_sizes': 1})

    users_photos = []

    for item in range(len(response['items'])):
        users_photos.append([response['items'][item]['likes']['count'],
                             response['items'][item]['sizes'][-1]['url']])

    photos = sorted(users_photos, key=lambda x: int(x[0]), reverse=True)

    return photos[:3]



    # print(get_user_info(636054))
    # print(search_possible_pair(1, 27, 35, 'Москва'))
    #print(get_photos(636054))
