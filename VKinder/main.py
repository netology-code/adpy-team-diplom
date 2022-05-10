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

count = 0
userAuth = False # пользователь пока не авторизован

while True:
    time.sleep(5)
    for event in longpoll.listen():

        if vk.is_event_equal_new_message(event.type) and event.to_me:

            request = event.text.lower()
            # делаем запрос в БД по event.user_id, на выходе получаем словарь (user_id, user_token, age, gender, city}
            user_data = get_user_data_from_db(event.user_id)

            if not userAuth and len(user_data) == 0: # если пользователя в БД нет, получаем его данные из профиля в ВК
                user_data = vk.get_user_data(vk_client, event.user_id)
                # запрашиваем в чат-боте токен пользователя (user_token) и добавляем его в словарь user_data
                vk.write_msg(vk_client, event.user_id, f'Введите свой токен для авторизации в БД')
                userAuth = True
                continue

            elif len(request) > 50:  # нужно поменять проверку для подтверждения, что введен именно токен
                user_data['user_token'] = request  # добавляем введенный токен к данным пользователя
                # добавляем нового пользователя в БД, на входе словарь (user_id, user_token, gender, city, age)
                add_new_user_to_db(user_data)

            else:
                #user_data = get_user_data_from_db(event.user_id)
                vk.write_msg(vk_client, event.user_id, f'''
                Введите команду: ищи людей / следующий / в избранное / показать избранное / пока
                '''
                )

                if request == "ищи людей":
                    partner_data = vk.search_people(user_data)
                    # выдать partner_data в читаемом формате в чат
                    message = partner_data['items'][count]['first_name'] \
                    + partner_data['items'][count]['last_name'] \
                    + vk.get_user_data(vk_client, partner_data['items'][count]['id']) \
                    # нужно дописать функцию для выдачи 3-х фото пользователя с наибольшим кол-вом лайков (photos.get)
                    + vk.get_user_photo(vk_client, partner_data['items'][count]['id'])
                    vk.write_msg(vk_client, event.user_id, message)

                elif request == "в избранное":
                    # попросить выбрать СЛЕДУЮЩИЙ / ИЗБРАННОЕ
                    add_to_favorites(user_id, partner_data['items'][count])
                    vk.write_msg(vk_client, event.user_id, f"Пользователь {result['items'][count]['id']} добавлен в избранное")

                elif request == "следующий":
                    count += 1

                elif request == "показать избранное":
                    message = display_favorites(user_id)
                    # надо добавить код для обработки message, чтобы инфа красиво выдавалась в чате
                    vk.write_msg(vk_client, event.user_id, message)

                elif request == "пока":
                    vk.write_msg(vk_client, event.user_id, f'Выполнение программы закончено')
                    break

                else:
                    # TODO: написать хелп если некорректный ввод
                    vk.write_msg(vk_client, event.user_id, "Не поняла вашего ответа...")