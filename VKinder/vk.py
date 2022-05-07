from datetime import date
from random import randrange
import time
import requests
from flask import Flask, request
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import socket
from threading import Thread
import listener


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def initialize_vk_client(token=''):
    if not token:
        # group_token
        token = '0958750174482253c31483e132a96c88aa890529dfe797f60e04beb97f8522441c78629e31f280bcd644c'
    return vk_api.VkApi(token=token)


def get_longpoll_from_vk(vk):
    return VkLongPoll(vk)


def write_msg(vk, user_id, message, additional_parameters=''):
    main_headers = {
        'user_id': user_id,
        'message': message,
        'random_id': randrange(10 ** 7),
    }

    vk.method('messages.send',
              dict(main_headers.items() + additional_parameters.items()) if additional_parameters else main_headers)


def calc_user_age(bdate):
    list_date = bdate.split('.')
    today = date.today()
    age = today.year - int(list_date[2]) - 1
    if today.month > int(list_date[1]) and today.day > int(list_date[0]):
        age += 1
    return age


def get_user_data(vk, user_id):
    res = vk.method('users.get', {'user_ids': user_id, 'fields': 'bdate, city, sex'})
    info = dict()
    info['gender'] = 'M' if res[0]['sex'] == 2 else 'W'
    info['city'] = res[0]['city']
    info['age'] = calc_user_age(res[0]['bdate'])
    info['id'] = user_id
    return info


def select_age(age, gender):
    # парням помоложе
    # девушкам постарше
    if gender == 'W':
        age_from = age
        age_to = age + 3
    else:
        age_from = age - 3
        age_to = age
    return [age_from, age_to]


def search_people(vk, info):
    age_from_to = select_age(info['age'], info['gender'])
    res = vk.method('users.search', {
        'city': info['city']['id'],
        # 2 = mens, 1 = women
        'sex': 1 if info['gender'] == 'M' else 2,
        'age_from': age_from_to[0],
        'age_to': age_from_to[1]
    })
    return res


def is_event_equal_new_message(event_type):
    return event_type == VkEventType.MESSAGE_NEW


def change_token(vk, new_token):
    vk = vk_api.VkApi(token=new_token)
