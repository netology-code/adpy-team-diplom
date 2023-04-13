import os
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from dotenv import load_dotenv, find_dotenv
import re
from vk_data_exchange import vk_api_data
from work_with_db import VKinderDB

load_dotenv(find_dotenv())
token = os.getenv('ACCESS_TOKEN')
input_data_list = []    #список входных данных полученных от пользователя для поиска
user_id_list = []   #значение user_id
chosen_candidate_list = []  #список избранных кандидатов

# генерация клавиатуры чат-бота
def menu_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button(label='\U00002605', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button(label='\U0000279C', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()
    keyboard.add_button(label='Показать \U00002605', color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()


# отправка сообщений в чат-бот
def write_msg(user_id, message, attachment=None, keyboard=None):
    vk_session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7),
                                        'attachment': attachment, 'keyboard': keyboard})


# получение команд от пользователя в чат-боте
def new_message(candidate_data=None):
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                user_id_list.append(event.user_id)
                request = event.text
                check_len_request = request.split(',')
                if request.lower() == 'начать':
                    write_msg(event.user_id,
                              'Добро пожаловать в Vkinder!\n\n'
                              'Введите данные для поиска через запятую в формате:\nВозраст, пол, город:')
                    # chosen_candidate_list.clear()
                elif request.lower() == 'стоп':
                    break
                elif candidate_data is not None:
                    if request.lower() == '\U0000279C':
                        generator_candidates(next(candidate_data))
                    elif request.lower() == '\U00002605':
                        vk_db = VKinderDB(next(candidate_data))
                        vk_db.add_favorite()
                    elif request.lower() == 'показать \U00002605':
                        pass
                    else:
                        write_msg(user_id_list[0], 'Неопознанная команда!')
                else:
                    if len(check_len_request) == 3:
                        input_data_list.append(request.title().strip())
                        return input_data_list
                    elif (request.lower() == '\U0000279C' or '\U00002605') and len(check_len_request) == 0:
                        write_msg(event.user_id,
                                  'Добро пожаловать в Vkinder!\n\n'
                                  'Введите данные для поиска через запятую в формате:\nВозраст, пол, город:')
                    else:
                        write_msg(event.user_id, 'Введен неверный формат данных! Повторите попытку:')


# форматирование входных данных, генерация словаря данных для поиска кандидатов
def formatting_data(data_list_):
    join_data_list = ','.join(data_list_)
    pattern_data_list = r'(\d+)\s*\W*([Муж|Жен]+)\w+\W*(\w+)'
    substitution_data_list = r'\1,\2,\3'
    format_data_list = re.sub(pattern_data_list, substitution_data_list, join_data_list, re.A)
    split_format_data_list = format_data_list.split(',')
    data_dict = {'age': int(split_format_data_list[0]),
                 'sex': split_format_data_list[1],
                 'city': split_format_data_list[2]}
    if data_dict['sex'] == 'Жен':
        data_dict['sex'] = 1
    else:
        data_dict['sex'] = 2
    return data_dict


# генерация информации о кандидатах в чат-бот
def generator_candidates(candidate_dict):
    if candidate_dict:
        if len(candidate_dict['photos_ids']) == 3:
            write_msg(user_id_list[0], f'{candidate_dict["first_name"]} '
                                       f'{candidate_dict["last_name"]}'
                                       f'\n{candidate_dict["link"]}',
                      attachment=f'photo{candidate_dict["id"]}'
                                 f'_{candidate_dict["photos_ids"][0]},'
                                 f'photo{candidate_dict["id"]}_'
                                 f'{candidate_dict["photos_ids"][1]},'
                                 f'photo{candidate_dict["id"]}_'
                                 f'{candidate_dict["photos_ids"][2]}',
                      keyboard=menu_keyboard())
            return candidate_dict
        elif len(candidate_dict['photos_ids']) == 2:
            write_msg(user_id_list[0], f'{candidate_dict["first_name"]} '
                                       f'{candidate_dict["last_name"]}'
                                       f'\n{candidate_dict["link"]}',
                      attachment=f'photo{candidate_dict["id"]}'
                                 f'_{candidate_dict["photos_ids"][0]},'
                                 f'photo{candidate_dict["id"]}_'
                                 f'{candidate_dict["photos_ids"][1]}',
                      keyboard=menu_keyboard())
        elif len(candidate_dict['photos_ids']) == 1:
            write_msg(user_id_list[0], f'{candidate_dict["first_name"]} '
                                       f'{candidate_dict["last_name"]}'
                                       f'\n{candidate_dict["link"]}',
                      attachment=f'photo{candidate_dict["id"]}'
                                 f'_{candidate_dict["photos_ids"][0]}',
                      keyboard=menu_keyboard())
        elif len(candidate_dict['photos_ids']) == 0:
            write_msg(user_id_list[0], f'{candidate_dict["first_name"]} '
                                       f'{candidate_dict["last_name"]}'
                                       f'\n{candidate_dict["link"]}',
                      keyboard=menu_keyboard())
        else:
            write_msg(user_id_list[0], 'По вашему запросу ничего не найдено!')


if __name__ == '__main__':
    vk_session = vk_api.VkApi(token=token)
    longpoll = VkLongPoll(vk_session)
    vk_search = vk_api_data.VKAPI()
    candidate_data = formatting_data(new_message())
    candidates = vk_search.search_candidates(candidate_data['age'], candidate_data['sex'], candidate_data['city'])
    generator_candidates(next(candidates))
    new_message(candidates)
    print(chosen_candidate_list)