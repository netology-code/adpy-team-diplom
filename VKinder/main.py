import time
import vk
import listener
from threading import Thread

# инициалиция
# возможно следует переделать вк в класс
vk_client = vk.initialize_vk_client()
longpoll = vk.get_longpoll_from_vk(vk_client)

# порты заблокированы, проверить не могу поэтому сделаю обычным вводом
# # это нужно, для того чтобы указывать в редирект адрес нужный адрес на котором у нас запущен сервис
# COMPUTER_IP = vk.get_ip()
# PORT = '8008'
#
# # запускаем сервер с целью возможности получения токена от пользователя (без его непосредственного участия)
# # TO/DO: доработать механизм обработки токена
# th = Thread(target=listener.run_listener)
# th.start()


APP_ID = '8158966'

access_token = ''
user_data = ''
# присутствует временно
# удалить сразу после функций записи/чтения токена из бд
tmp_token = '61255e4bfa771fff688109f5422812c7791a03ab8046a195c23add5a30f87042c168c7bdbfdfe5677f8ab'
# ---
#

# cтандартные кнопки для сообщения
kb_candidate_commands = vk.create_basic_keyboard()

help_message = 'Напишите команду "ищи людей" для начала поиска "кандидатов"'

def token_existed(user_data):
    # TODO Sergey: сделать проверку (вероятнее всего тут нужно обращаться в бд,
    # или же чекать из юзер инфо
    return bool(tmp_token)


def show_authorization_message(vk_cl, user_id):
    vk.write_msg(vk_cl, user_id,
                 f"Для использования бота нужно пройти аутентификацию, ее можно пройти тут:\n"
                 f"https://oauth.vk.com/authorize?client_id={APP_ID}&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=groups,offline&response_type=token&v=5.52\n"
                 f"После получения токена отправь его мне (лучше полную ссылку в браузерной строке)"
                 )



while True:
    time.sleep(5)

    for event in longpoll.listen():
        if vk.is_event_equal_new_message(event.type):
            if event.to_me:

                # кто к нам обращается ---
                # TODO Sergey: чекнуть ли есть данные по этому юзеру
                user_data_existed = False
                if user_data_existed:
                    # TODO Sergey: если существует - присваиваем данные user_data
                    # user data = db.get_user_info(event.user_id) (example)
                    pass
                else:
                    # тут получаю первоначальную инфу БЕЗ ТОКЕНА
                    user_data = vk.get_user_data(vk_client, event.user_id)
                    # TODO Sergey: записать данные в бд
                # --- кто к нам обращается

                request = event.text.lower()
                has_access_token = request.find('access_token')
                # TODO: прикрутить кнопки

                if request == "start":
                    # TODO Sergey: тут в теории должна быть проверка на токен
                    # event.user_id = ид юзера (вк), его можно использовать для поиска
                    # т.е. если пользователь без токена пишет "старт"
                    if token_existed(event.user_id):
                        vk.write_msg(vk_client, event.user_id, help_message)
                    else:
                        vk.write_msg(vk_client, event.user_id,
                                     f"Привет, для использования бота нужно пройти аутентификацию, ее можно пройти тут:\n"
                                     f"https://oauth.vk.com/authorize?client_id={APP_ID}&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=groups,offline&response_type=token&v=5.52\n"
                                     f"После получения токена отправь его мне (лучше полную ссылку в браузерной строке)")

                elif request == "ищи людей":
                    # TODO Sergey: проверить ли есть токен в бд
                    # TODO Sergey: получить токен (или запросить авторизоваться)

                    # если был получен ранее нормальный токен
                    if token_existed(user_data):
                        vk_personal = vk_client = vk.initialize_vk_client(tmp_token)
                        result = vk.search_people(vk_personal, user_data)
                        current_user = result['items'][1]
                        # !метод работает только с персональным токеном
                        message = vk.make_message_about_another_user(current_user, vk_client, event.user_id)
                        str_attachments = vk.find_photos(current_user['id'], vk_personal)
                        # тут короче фигня какая-то
                        # после получения vk_personal vk_client ломается
                        # поэтому я его тут повторно инициализирую
                        # TODO: найти альтернативу строчке ниже
                        vk_client = vk.initialize_vk_client()
                        # TODO: прикрепить кнопки (в тек момент там только 1 кнопка и то не та что нужно)
                        vk.write_msg(vk_client, event.user_id, message,
                                     {
                                         'attachment': str_attachments,
                                         'keyboard': kb_candidate_commands.get_keyboard()
                                     })
                        # сейчас вывожу просто первого юзера чисто разработать механизм
                        # TODO: придумать алгоритм вывода "кандидатов"
                    else:
                        show_authorization_message(vk_client, event.user_id)

                elif has_access_token:
                    start = has_access_token + len('access_token=')
                    end = request.find('&', has_access_token)
                    if 82 < len(access_token) < 87:
                        access_token = request[start:(end if end else 0)]
                    else:
                        vk.write_msg(vk_client, event.user_id, help_message)
                elif 82 < len(request) < 87:
                    # вероятнее всего человек написал только токен
                    # у моего токена была длина 85, я хз он меняется там или нет, поэтому взял с зазором
                    access_token = request
                else:
                    vk.write_msg(vk_client, event.user_id, help_message)

                if access_token and user_data:
                    # TODO Sergey: записать токен в бд
                    tmp_token = access_token
                    vk.write_msg(vk_client, event.user_id, "Токен успешно сохранён!")
                    access_token = ''
                    # возможно стоит проверить токен на "работоспособность"
