import time
import vk
import listener
from threading import Thread

# инициалиция
# возможно следует переделать вк в класс
vk_client = vk.initialize_vk_client()
longpoll = vk.get_longpoll_from_vk(vk_client)

# порты заблочены, проверить не могу поэтому сделаю обычным инпутом
# # это нужно для того чтобы указывать в редирект адресс нужный адресс на котором у нас запущен сервис
# COMPUTER_IP = vk.get_ip()
# PORT = '8008'
#
# # запускаем сервера с целью возможности получения токена от пользователя
# # TO/DO: доработать механизм обработки токена (в слушателе)
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
while True:
    time.sleep(5)

    for event in longpoll.listen():
        if vk.is_event_equal_new_message(event.type):
            # TODO:получить данные юзера (из бд)
            user_data_existed = False
            if user_data_existed:
                pass
            else:
                user_data = vk.get_user_data(vk_client, event.user_id)
                # TODO: записать данные в бд

            if event.to_me:
                request = event.text.lower()
                has_access_token = request.find('access_token')
                # TODO: прикрутить кнопки

                if request == "start":
                    # TODO: тут в теории должна быть проверка на токен
                    # и выводить сообщение ниже при условии отсутствия персонального токена
                    vk.write_msg(vk_client, event.user_id,
                                 f"Привет, для использования бота нужно пройти аутентификацию, ее можно пройти тут:\n"
                                 f"https://oauth.vk.com/authorize?client_id={APP_ID}&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=groups,offline&response_type=token&v=5.52\n"
                                 f"После получения токена отправь его мне (лучше полную ссылку в браузерной строке)")
                    # TODO: если токен существует то должен быть другой вывод
                elif request == "ищи людей":
                    # TODO: проверить ли есть токен в бд
                    # TODO: получить токен (или запросить авторизоваться)

                    # если был получен ранее нормальный токен
                    if tmp_token:
                        vk_personal = vk_client = vk.initialize_vk_client(tmp_token)
                        result = vk.search_people(vk_personal, user_data)
                        # тут короче фигня какая-то
                        # после получения vk_personal vk_client ломается
                        # поэтому я его тут повторно инициализирую
                        # TODO: найти альтернативу строчке ниже
                        vk_client = vk.initialize_vk_client()
                        vk.write_msg(vk_client, event.user_id,
                                     f"Было найдено {result['count']} человек.")
                    # если токен не был найден
                    else:
                        vk.write_msg(vk_client, event.user_id,
                                     f"Для использования бота нужно пройти аутентификацию, ее можно пройти тут:\n"
                                     f"https://oauth.vk.com/authorize?client_id={APP_ID}&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=groups,offline&response_type=token&v=5.52\n"
                                     f"После получения токена отправь его мне (лучше полную ссылку в браузерной строке)")
                elif has_access_token:
                    start = has_access_token + len('access_token=')
                    end = request.find('&', has_access_token)
                    access_token = request[start:end if end else 0]
                elif 82 < len(request) < 87:
                    # вероятнее всего человек написал только токен
                    # у моего токена была длина 85, я хз он меняется там или нет, поэтому взял с зазором
                    access_token = request
                else:
                    # TODO: написать хелп если некорректный ввод
                    vk.write_msg(vk_client, event.user_id, "Не поняла вашего ответа...")

                if access_token and user_data:
                    # TODO: записать токен в бд
                    tmp_token = access_token
                    vk.write_msg(vk_client, event.user_id, "Токен успешно сохранён!")
                    access_token = ''

