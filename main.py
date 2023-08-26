import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll
import VKinder_Api
from VKinder_DB import *
from VKinder_Api import get_photo, get_info, get_search, write_msg, get_user_token

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

vk = vk_api.VkApi(token=VKinder_Api.token)
longpoll = VkLongPoll(vk)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        info_user = get_info(event.user_id)
        token = get_user_token()
        if event.to_me:
            request = event.text
            add_user(event.user_id, info_user['first_name'], info_user['gender'], info_user['age'], info_user['city']['title'])
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
                                    add_offer(event.user_id, int(profile['id_offer']), profile['first_name'], profile['last_name'], profile['gender'], profile['agе'], profile['city']['title'])
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
                                                    add_favorite(event.user_id, int(profile['id_offer']))
                                                    write_msg(event.user_id, f"Я добавил {profile['first_name']} в ваш список избранного!")
                                                    break
                                                elif request == "В черный список!":
                                                    add_black_list(event.user_id, int(profile['id_offer']))
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
                    add_offer(event.user_id, int(profile['id_offer']), profile['first_name'], profile['last_name'],
                              profile['gender'], profile['agе'], profile['city']['title'])
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
                                    add_favorite(event.user_id, int(profile['id_offer']))
                                    write_msg(event.user_id,
                                              f"Я добавил {profile['first_name']} в ваш список избранного!")
                                    break
                                elif request == "В черный список!":
                                    add_black_list(event.user_id, int(profile['id_offer']))
                                    write_msg(event.user_id,
                                              f"Я больше не буду показывать вам профиль {profile['first_name']} !")
                                    break
                write_msg(event.user_id, "У меня на этом все!", keyboard_restart.get_keyboard())
            elif request == "Хватит!" or request == "Нет спасибо!":
                write_msg(event.user_id, "Ноу проблем...")
            else:
                write_msg(event.user_id, "Не понял вашего ответа...")
