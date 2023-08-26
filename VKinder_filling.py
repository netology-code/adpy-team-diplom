from VKinder_DB import add_user, add_offer, add_photo
from main import get_search, get_info


def filling_db(user_id, offset):
    user_info = get_info(user_id)
    offer_info = get_info(user_id)
    photo_info = get_search(user_info['city']['id'], user_info['age'], user_info['gender'], offset)

    add_user(user_id, user_info['first_name'], user_info['sex'], user_info['age'], user_info['city_name'])

    for dict in offer_info:
        add_offer(user_id, dict['id_offer'], dict['first_name'], dict['last_name'], dict['sex'], dict['age'], user_info['city'])

    for dict_p in photo_info:
        add_photo(dict_p['photo_link'], dict_p['url_profile'])
