import time
import vk
import listener
from threading import Thread

# инициалиция
vk_client = vk.initialize_vk_client()
longpoll = vk.get_longpoll_from_vk(vk_client)

# это нужно для того чтобы указывать в редирект адресс нужный адресс на котором у нас запущен сервис
COMPUTER_IP = vk.get_ip()
PORT = '8008'

# запускаем сервера с целью возможности получения токена от пользователя
# TODO: доработать механизм обработки токена (в слушателе)
th = Thread(target=listener.run_listener)
th.start()

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

                if request == "привет":
                    vk.write_msg(vk_client, event.user_id, f"Хай, {event.user_id}")
                elif request == "пока":
                    vk.write_msg(vk_client, event.user_id, "Пока((")
                elif request == "ищи людей":
                    # TODO: проверить ли есть токен в бд
                    # TODO: получить токен
                    # TODO: или сформировать новый если нет

                    # поиск людей не работает так как нужен не коммьюнити токен
                    # TODO: доработать после доработки токенов
                    result = vk.search_people(user_data)
                    vk.write_msg(vk_client, event.user_id, "Пока((")
                else:
                    # TODO: написать хелп если некорректный ввод
                    vk.write_msg(vk_client, event.user_id, "Не поняла вашего ответа...")