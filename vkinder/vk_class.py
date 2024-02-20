import json
from random import randrange
import datetime
from datetime import date
import asyncio
from aiohttp import ClientSession

from threading import Thread


class VkClass:
    def __init__(self, vk_personal, vk_group, orm, personal_token):
        self.personal_token = personal_token
        self.vk_group = vk_group
        self.personal_vk = vk_personal
        self.orm = orm
        self.testers = []
        self.current_state = 0
        self.hometown = ''
        self.partner_age = 0
        self.partner_info = []
        self.partner_gender = 1

    @staticmethod
    def partners_gen(partners_list):
        for person in partners_list:
            yield person

    @staticmethod
    def filter_friends(partners_list):
        if 'bdate' in partners_list.keys():
            if not partners_list['is_friend'] and not partners_list['is_closed'] and len(partners_list['bdate']) > 8:
                return True
            else:
                return False
        else:
            return False

    def send_keyboard(self, user_id, message, keyboard):
        self.vk_group.method('messages.send',
                             {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7),
                              'keyboard': keyboard})

    def get_photos(self, person):
        all_photos = []
        for image in self.personal_vk.method('photos.get',
                                             {'owner_id': person['id'],
                                              'album_id': "profile", "extended": "1"})['items']:
            all_photos.append([image["likes"]["count"], image["id"]])
        all_photos.sort()
        all_photos.reverse()
        best_images = []
        for image in all_photos[:3]:
            best_images.append(f"photo{person['id']}_{image[1]}")
        return best_images

    def build_url_values(self, ids):
        values = {'access_token': self.personal_token,
                  'v': '5.199',
                  'owner_id': ids,
                  'album_id': 'profile',
                  'extended': '1'
                  }
        return values

    async def async_get_photo(self, ids, session):
        url_values = self.build_url_values(ids)
        url = 'https://api.vk.ru/method/photos.get'
        try:
            async with session.get(url, params=url_values) as response:

                # Считываем json
                if response.ok:
                    resp = await response.text()
                    js = json.loads(resp)
                    if 'error' not in resp:
                        photo_list_users = [x for x in js['response']['items'] if x]
                else:
                    return None

            all_photos = []
            for image in photo_list_users:
                all_photos.append([image["likes"]["count"], image["id"]])
            all_photos.sort()
            all_photos.reverse()
            for image in all_photos[:3]:
                self.photo_data.append(f"photo{ids}_{image[1]}")

        except Exception as ex:
            print(f'Error: {ex} IDS {ids} - {js}')

    async def task_get_photo(self, ids, personal_token):
        tasks = []
        ses = ClientSession(headers={'Authorization': f'Bearer {personal_token}'})
        async with ses as session:
            task = asyncio.ensure_future(self.async_get_photo(ids, session))
            await asyncio.sleep(.33)
            tasks.append(task)

            responses = asyncio.gather(*tasks)
            await responses
            del responses
            await session.close()

    def next_partner(self, event, count, age, offset):
        if self.testers is None or not self.testers:
            self.testers = \
                self.personal_vk.method('users.search',
                                        values={'count': count, 'offset': offset, 'sex': self.partner_gender,
                                                'has_photo': 1,
                                                'hometown': self.hometown,
                                                'age_from': age, 'age_to': age,
                                                'fields': 'is_friend, sex, bdate'})['items']
        self.testers = list(filter(self.filter_friends, self.testers))

        for person in self.testers:
            # print(person['id'])
            self.photo_data = []
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.task_get_photo(person['id'], self.personal_token))
            if len(self.photo_data) < 3:
                continue
            self.orm.add_partner(event.user_id, person['id'],
                                 {'name': person['first_name'], 'surname': person['last_name'],
                                  'gender': person['sex'],
                                  'age': int(str(date.today())[:4]) - int(person['bdate'][-4:]),
                                  'foto': self.photo_data, 'link': f'https://vk.com/id{person["id"]}'}
                                 )

        self.testers = []

    def send_photos(self, user_id, message, attachment):
        self.vk_group.method('messages.send',
                             {'user_id': user_id, 'message': message, 'attachment': attachment,
                              'random_id': randrange(10 ** 7), })

    def write_msg(self, user_id, message):
        self.vk_group.method('messages.send',
                             {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })

    def check_user(self, event, first_keyboard, active_keyboard):
        if self.orm.get_user_id(event.user_id) is None:
            user_data = self.personal_vk.method(method='users.get',
                                                         values={'user_ids': event.user_id,
                                                                 'fields': 'sex,city,bdate'})
            self.check_bdate(event, user_data, first_keyboard, active_keyboard)
        else:
            self.first_state(event, first_keyboard, active_keyboard)

    def check_bdate(self, event, user_data, first_keyboard, active_keyboard):
        if 'bdate' in user_data[0].keys():
            if len(user_data[0]['bdate']) > 8:
                user_age = int(str(date.today())[:4]) - int(user_data[0]['bdate'][-4:])
                self.orm.add_user(vk_id=event.user_id,
                                  data={'age': user_age, 'city': user_data[0]['city']['title'],
                                        'gender': user_data[0]['sex']})
                self.first_state(event, first_keyboard, active_keyboard)
            else:
                self.write_msg(event.user_id, "Введите ваш возраст")
                self.current_state = 4
                self.orm.add_state(event.user_id, 4)
        else:
            self.write_msg(event.user_id, "Введите ваш возраст")
            self.current_state = 4
            self.orm.add_state(event.user_id, 4)

    def first_state(self, event, first_keyboard, active_keyboard):
        request = event.text
        if request.lower() == "начать":
            self.send_keyboard(event.user_id, 'Привет!!!', first_keyboard.get_keyboard())
        elif request.lower() == "показать избранных":
            self.write_msg(event.user_id, f'❤ Ваш список избранных ❤')
            for partner in self.orm.get_favorite_list(self.orm.get_user_id(event.user_id)):
                self.partner_info = self.orm.get_partner(partner)
                print(self.partner_info)
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), self.partner_info[3][0])
            self.write_msg(event.user_id, f'❤❤❤❤❤❤')
        elif request.lower() == "показать заблокированных":
            self.write_msg(event.user_id, f'Список заблокированных вами пользователей❤')
            for partner in self.orm.get_blacklist(self.orm.get_user_id(event.user_id)):
                self.partner_info = self.orm.get_partner(partner)
                print(self.partner_info)
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), self.partner_info[3][0])
        elif request.lower() == "подобрать":
            self.orm.clear_partner_all(self.orm.get_user_id(event.user_id))
            self.send_keyboard(event.user_id, 'В каком городе будем искать?', first_keyboard.get_empty_keyboard())
            self.current_state += 1
            self.orm.add_state(event.user_id, 1)
        elif request.lower() == "автоподбор":
            print('auto')
            self.orm.clear_partner_all(self.orm.get_user_id(event.user_id))
            self.write_msg(event.user_id, 'Поиск будет выполнен на основе данных вашего профиля')
            searh_data = self.orm.get_search_data(event.user_id)
            self.partner_age = searh_data[0]
            self.partner_gender = searh_data[1]
            self.hometown = searh_data[2]
            self.next_partner(event, 25, self.partner_age, 0)
            self.send_keyboard(event.user_id, 'Пользователи найденные по вашему запросу',
                               active_keyboard.get_keyboard())
            self.partner_info = self.orm.get_random_partner()
            self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
            self.current_state = 3
            self.orm.add_state(event.user_id, 3)
        else:
            self.write_msg(event.user_id, "Не поняла вашего ответа... Можете повторить еще раз?")

    def second_state(self, event):
        request = event.text
        self.hometown = request
        print(self.hometown)
        self.write_msg(event.user_id, 'Введите возраст партнера')
        self.current_state += 1
        self.orm.add_state(event.user_id, 2)

    def third_state(self, event, active_keyboard):
        request = event.text
        self.partner_age = int(request)
        print(self.partner_age)

        # # фиксируем и выводим время старта работы кода
        # start = datetime.datetime.now()
        # print('Время старта: ' + str(start))

        # код, время работы которого измеряем

        # фиксируем и выводим время окончания работы кода
        # finish = datetime.datetime.now()
        # print('Время окончания: ' + str(finish))
        #
        # # вычитаем время старта из времени окончания
        # print('Время работы: ' + str(finish - start))

        # Thread(target=self.next_partner, args=(event, 1000, self.partner_age - 1, 25)).start()
        # Thread(target=self.next_partner, args=(event, 1000, self.partner_age, 25)).start()
        # Thread(target=self.next_partner, args=(event, 1000, self.partner_age + 1, 25)).start()
        for age in range(self.partner_age - 1, self.partner_age + 2):
            start = datetime.datetime.now()
            self.next_partner(event, 1000, age, 0)
            finish = datetime.datetime.now()
            print('Время работы: ' + str(finish - start))
        # # фиксируем и выводим время окончания работы кода
        # finish = datetime.datetime.now()
        # print('Время окончания: ' + str(finish))
        #
        # # вычитаем время старта из времени окончания
        # print('Время работы: ' + str(finish - start))
        self.send_keyboard(event.user_id, 'Всё готово, можно начинать', active_keyboard.get_keyboard())
        self.partner_info = self.orm.get_random_partner()
        self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
        self.current_state += 1
        self.orm.add_state(event.user_id, 3)

    def fourth_state(self, event, first_keyboard):
        request = event.text
        user_age = int(request)
        user_data = self.personal_vk.method(method='users.get',
                                            values={'user_ids': event.user_id, 'fields': 'sex,city,bdate'})
        self.orm.add_user(vk_id=event.user_id,
                          data={'age': user_age, 'city': user_data[0]['city']['title'],
                                'gender': user_data[0]['sex']})
        self.send_keyboard(event.user_id, 'Начинаем!', first_keyboard.get_keyboard())
        self.current_state = 0
        self.orm.add_state(event.user_id, 0)

    def active_state(self, event, first_keyboard):
        request = event.text
        if request.lower() == 'следующий':
            self.orm.clear_partner_row(self.orm.get_user_id(event.user_id))
            self.partner_info = self.orm.get_random_partner()
            if self.partner_info is None:
                self.next_partner(event, 25, self.partner_age, 0)
                self.partner_info = self.orm.get_random_partner()
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
            else:
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
        elif request.lower() == 'выйти':
            self.orm.add_state(event.user_id, 0)
            self.current_state = 0
            self.send_keyboard(event.user_id, 'Всего доброго! До скорых встреч!!', first_keyboard.get_keyboard())
        elif request.lower() == 'в избранное':
            self.orm.add_favorite(self.orm.get_last_user_id(self.orm.get_user_id(event.user_id)))
            self.partner_info = self.orm.get_random_partner()
            if self.partner_info is None:
                self.next_partner(event, 25, self.partner_age, 0)
                self.partner_info = self.orm.get_random_partner()
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
            else:
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
        elif request.lower() == 'заблокировать':
            self.orm.add_blacklist(self.orm.get_last_user_id(self.orm.get_user_id(event.user_id)))
            self.partner_info = self.orm.get_random_partner()
            if self.partner_info is None:
                self.next_partner(event, 25, self.partner_age, 0)
                self.partner_info = self.orm.get_random_partner()
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
            else:
                self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
        elif request.lower() == 'лайк':
            self.personal_vk.method('likes.add',
                                    values={'type': 'photo', 'owner_id': '178546945', 'item_id': '457246150'})
