import os
import random

import vk_api
import requests

from vk_api import VkUpload
from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from ORMTableStructure import Cities
from CheckBD.CheckDBORM import CheckDBORM
from Repository.ORMRepository import ORMRepository


load_dotenv()
token = os.getenv(key='ACCESS_TOKEN')
token_api = os.getenv(key='ACCESS_TOKEN_API')
vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session)
upload = VkUpload(vk_session.get_api())
repository = ORMRepository()


def send_message(event: vk_api.longpoll.Event,
                 message: str,
                 keyboard: vk_api.keyboard.VkKeyboard = None,
                 photo_attachments: list = None) -> None:

    """
    Выводим сообщения пользователю

    Вводные параметры:
    event: событие, задаваемое в рамках API Longpoll
    message: сообщение, которое хотим вывести пользователю
    keyboard: экземпляр класса VkKeyboard (нужен для привязки клавиатур)
    photo_attachments: список объектов, приложенных к комментарию
    относительно фотографий (нужен для привязки фотографий)

    Структура photo_attachments:
    <type><owner_id>_<media_id> (пример: photo-225663449_457239297)
    <type> — тип медиа-вложения
    <owner_id> — идентификатор владельца медиа-вложения
    <media_id> — идентификатор медиа-вложения
    """

    dict_params = {
        'user_id': event.user_id,
        'message': message,
        'random_id': random.randint(-2147483648, +2147483648)
    }

    if keyboard:
        dict_params.update({
            'keyboard': keyboard.get_keyboard()
        })

    if photo_attachments:
        dict_params.update({
            'attachment': ','.join(photo_attachments)
        })

    vk_session.method('messages.send', dict_params)


def get_favorites_data(event: vk_api.longpoll.Event) -> list[dict]:

    """
    Выводит данных, находящиеся в таблице favorites

    Вводной параметр:
    event: событие, задаваемое в рамках API Longpoll

    Выводной параметр:
    favorites_data: список словарей, содержащий данные таблицы favorites
    """

    favorites_data = repository.get_favorites(event.user_id)
    if favorites_data:
        return favorites_data


def get_cities_data() -> list[dict]:

    """
    Выводит данных, содержащиеся в таблице cities

    Выводной параметр:
    cities_data: список словарей, содержащий данные таблицы cities
    """

    cities_data = repository.get_table_values(Cities)
    if cities_data:
        return cities_data


def show_candidate_buttons() -> vk_api.keyboard.VkKeyboard:

    """
    Выводит кнопки, отвечающие за выбор пользователя из раздела "Избранное"

    Выводной параметр:
    keyboard: экземпляр класса VkKeyboard
    """

    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button('Назад', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Вперед', color=VkKeyboardColor.PRIMARY)

    keyboard.add_line()
    keyboard.add_button('Отмена', color=VkKeyboardColor.POSITIVE)

    return keyboard


def get_photo_attachments(photos_url: list[str]) -> list[str]:

    """
    Позволяет на основе списка URL-ссылок:
    1) получить адрес сервера для загрузки фотографий
    2) сохранить фото в сообщении после её успешной загрузки на сервер
    3) вывести список объектов, приложенных к комментарию (photo_attachments)

    Вводной параметр:
    photos_url: список URL-ссылок

    Выводной параметр:
    photo_attachments: список объектов, приложенных к комментарию по фото
    ([<type><owner_id1>_<media_id1>, <type><owner_id2>_<media_id2>, ...])
    """

    photo_attachments = []
    for photo_idx, photo_url in enumerate(photos_url):
        if photo_url is not None:

            # GET-запрос и получение контента из URL-ссылки
            response = requests.get(photo_url)
            files = {'photo': ('photo.jpg', response.content)}

            # Вызов метода photos.getMessagesUploadServer. Он позволяет
            # получить адрес сервера для загрузки фотографий (upload_url)
            upload_server = vk_session.method('photos.getMessagesUploadServer')
            upload_url = upload_server.get('upload_url')

            # POST-запрос относительно адреса upload_url и вывод данных по фото
            upload_response = requests.post(upload_url, files=files)
            photo_data = upload_response.json()

            # Подготовка параметров, полученных после загрузки фотографии на сервер:
            # 1) фотография в формате multipart/form-data (photo)
            # 2) идентификатор сервера, на который загружена фотография (server)
            # 3) хеш фотографии (hash)
            photo_params = {
                'photo': photo_data['photo'],
                'server': photo_data['server'],
                'hash': photo_data['hash']
            }

            # Вызов метода photos.saveMessagesPhoto. Позволяет сохранить фото
            # в сообщении после её успешной загрузки на сервер.
            saved_photo = vk_session.method('photos.saveMessagesPhoto',
                                            photo_params)[0]

            # Формирование объекта, содержащего информацию по фотографии
            # в формате <type><owner_id>_<media_id> (photo_attachment)
            owner_id = saved_photo.get('owner_id')
            media_id = saved_photo.get('id')
            photo_attachment = f"photo{owner_id}_{media_id}"
            photo_attachments.append(photo_attachment)

    return photo_attachments


def show_favorite_candidate(event: vk_api.longpoll.Event,
                            favorites_data: list[dict],
                            favorite_idx: int) -> None:

    """
    Позволяет вывести в сообщении кандидата из раздела "Избранное"

    Вводной параметр:
    event: событие, задаваемое в рамках API Longpoll
    favorites_data: список словарей, содержащий данные таблицы favorites
    favorite_idx: идентификатор словаря, содержащегося внутри списка favorites_data
    """

    favorite_dict = favorites_data[favorite_idx]
    send_message(event, 'Вывожу кандидата из раздела "Избранное"')

    photos_url = [
        favorite_dict.get('photo1'),
        favorite_dict.get('photo2'),
        favorite_dict.get('photo3')
    ]

    photo_attachments = get_photo_attachments(photos_url)
    send_message(event=event, message=f'🌠 Фотографии 🌠',
                 photo_attachments=photo_attachments)

    first_name = favorite_dict.get('first_name')
    last_name = favorite_dict.get('last_name')
    city_id = favorite_dict.get('city_id')
    cities_data = get_cities_data()

    keyboard = show_candidate_buttons()
    msg_candidate = f'🌠 ФИО: {first_name} {last_name} 🌠'

    if cities_data:
        for dict_city in cities_data:
            if dict_city.get('id') == city_id:
                msg_city = f'🌠 Город: {dict_city.get("name")} 🌠'
                send_message(event=event, message=msg_candidate)
                send_message(event=event, message=msg_city, keyboard=keyboard)
                break
    else:
        send_message(event=event, message=msg_candidate, keyboard=keyboard)


if __name__ == '__main__':

    favorite_idx = 0

    if CheckDBORM().check_db():
        for event in VkLongPoll(vk_session).listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                text = event.text.lower()

                # Вывод списка словарей, содержащего данные таблицы favorites
                favorites_data = get_favorites_data(event)

                # Проверка наличия данных в таблице favorites и подсчет
                # пользователей, содержащихся в списке словарей favorites_data
                if favorites_data:
                    total_favorites = len(favorites_data)

                    # Начало работы с пользователем внутри раздела "Избранное"
                    if text == 'favorites':
                        text_message = f'Отлично! Давай посмотрим, что у тебя находится в разделе "Избранное" 🌠.'
                        send_message(event, text_message)
                        show_favorite_candidate(event, favorites_data, favorite_idx)

                    # Обработка резульата ввода кнопки "Назад"
                    if text == 'назад':
                        if total_favorites != 1:

                            # Проработка двух случаев:
                            # 1) нажатие на кнопку во время просмотра второго или последующего кандидата (if)
                            # 2) нажатие на кнопку во время просмотра первого кандидата (else)
                            if favorite_idx != 0:
                                favorite_idx -= 1
                                show_favorite_candidate(event, favorites_data, favorite_idx)
                            else:
                                text_message = 'Для перехода к следующему пользователю необходимо нажать кнопку "Вперед"'
                                send_message(event, text_message)

                        # Нажатие на кнопку во время просмотра единственного кандидата
                        else:
                            text_message = 'У тебя только один пользователь находится в разделе "Избранное"'
                            send_message(event, text_message)

                    # Обработка резульата ввода кнопки "Вперед"
                    if text == 'вперед':
                        if total_favorites != 1:

                            # Проработка двух случаев:
                            # 1) нажатие на кнопку во время просмотра предполеднего или более раннего кандидата (if)
                            # 2) нажатие на кнопку во время просмотра последнего кандидата (else)
                            if favorite_idx != total_favorites - 1:
                                favorite_idx += 1
                                show_favorite_candidate(event, favorites_data, favorite_idx)
                            else:
                                text_message = 'Все пользователи из раздела "Избранное" уже просмотрены'
                                send_message(event, text_message)

                        # Нажатие на кнопку во время просмотра единственного кандидата
                        else:
                            text_message = 'У тебя только один пользователь находится в разделе "Избранное"'
                            send_message(event, text_message)

                    # Обработка резульата ввода кнопки "Отмена"
                    if text == 'отмена':
                        text_message = 'Поиск избранных завершен. Возвращаемся в раздел "Начать поиск"'
                        send_message(event, text_message)

                # Вывод информации об отсутствии данных
                else:
                    text_message = 'Твоя база с избранными пока не заполнена. Возвращаемся в раздел "Начать поиск"'
                    send_message(event, text_message)
