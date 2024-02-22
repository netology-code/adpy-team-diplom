import json
from random import randrange
import datetime
from datetime import date
import asyncio
from aiohttp import ClientSession
from vkinder.vk_bot_state import BotState
from vkinder.vk_keyboard import create_first_keyboard, create_active_keyboard, create_empty_keyboard


first_keyboard = create_first_keyboard()
active_keyboard = create_active_keyboard()
empty_keyboard = create_empty_keyboard()


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

    # def send_keyboard(self, user_id, message, keyboard):
    #     self.vk_group.method('messages.send',
    #                          {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7),
    #                           'keyboard': keyboard.get_keyboard()})
    def write_msg(self, user_id, message, keyboard=None):
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

    # def write_msg(self, user_id, message, keyword=None):
    #     self.vk_group.method('messages.send',
    #                          {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })

    def check_user(self, event):
        if not self.orm.get_user_id(event.user_id):
            self.orm.add_user(event.user_id)
            self.orm.add_state(event.user_id, BotState.check_bdate.value)
            self.check_bdate(event.user_id, event.message)
        else:
            self.orm.add_state(event.user_id, BotState.search_state.value)

    # def check_user(self, event, first_keyboard, active_keyboard):
    #     if self.orm.get_user_id(event.user_id) is None:
    #         self.check_bdate(event, first_keyboard, active_keyboard)
    #     else:
    #         self.first_state(event, first_keyboard, active_keyboard)

    def check_bdate(self, vk_user_id, msg):
        user_data = self.personal_vk.method(method='users.get',
                                            values={'user_ids': vk_user_id,
                                                    'fields': 'sex,city,bdate'})
        self.orm.update_user(vk_id=vk_user_id,
                             data={'city': user_data[0]['city']['title'],
                                   'gender': user_data[0]['sex']})

        try:
            req_err = False
            if 'bdate' in user_data[0].keys():
                if len(user_data[0]['bdate']) > 6:
                    user_age = int(str(date.today())[:4]) - int(user_data[0]['bdate'][-4:])
                    self.orm.update_user(vk_id=vk_user_id,
                                         data={'age': user_age})
                    self.orm.add_state(vk_user_id, BotState.search_state.value)
                    self.main_state(vk_user_id)
                    return
            if msg.isdigit() is not True:
                self.write_msg(vk_user_id, 'Проверьте в профиле ваш возраст (должно быть целое число).',
                               keyboard=empty_keyboard)
                req_err = True
            if req_err is False:
                self.orm.update_user(vk_id=vk_user_id,
                                     data={'age': msg})
                self.orm.add_state(vk_user_id, BotState.search_state.value)
                self.main_state(vk_user_id)
                return
            raise ValueError
        except ValueError:
            ValueError("Ошибка проверки введенного запроса пользователя!")
            self.write_msg(vk_user_id, 'Введите ваш возраст.')

    def empty_state(self):
        self.orm.check_database()

    def end_discussion(self, vk_user_id):
        self.write_msg(vk_user_id, "Всего доброго! До скорых встреч!", keyboard=first_keyboard)
        self.orm.add_state(vk_user_id, BotState.search_state.value)

    def main_state(self, vk_user_id):
        user_name = self.personal_vk.method(method='users.get',
                                            values={'user_ids': vk_user_id})
        self.write_msg(vk_user_id, f'Привет {user_name[0]["first_name"]} !', keyboard=first_keyboard)
        self.orm.add_state(vk_user_id, BotState.search_state.value)

    def show_favorite(self, event):
        self.write_msg(event.user_id, f'❤ Ваш список избранных ❤')
        for partner in self.orm.get_favorite_list(self.orm.get_user_id(event.user_id)):
            self.partner_info = self.orm.get_partner(partner)

            self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), self.partner_info[3][0])
        self.write_msg(event.user_id, f'❤❤❤❤❤❤')

    def add_favorite(self, event):
        self.orm.add_favorite(self.orm.get_last_user_id(self.orm.get_user_id(event.user_id)))
        self.partner_info = self.orm.get_random_partner()
        if self.partner_info is None:
            self.next_partner(event, 25, self.partner_age, 0)
            self.partner_info = self.orm.get_random_partner()
            self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
        else:
            self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))

    def show_blacklist(self, event):
        for partner in self.orm.get_blacklist(self.orm.get_user_id(event.user_id)):
            self.partner_info = self.orm.get_partner(partner)
            print(self.partner_info)
            self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), self.partner_info[3][0])

    def add_blacklist(self, event):
        self.orm.add_blacklist(self.orm.get_last_user_id(self.orm.get_user_id(event.user_id)))
        self.partner_info = self.orm.get_random_partner()
        if self.partner_info is None:
            self.next_partner(event, 25, self.partner_age, 0)
            self.partner_info = self.orm.get_random_partner()
            self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
        else:
            self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))

    def get_city(self, event):
        self.write_msg(event.user_id, "В каком городе будем искать?", keyboard=empty_keyboard)
        self.orm.add_state(event.user_id, BotState.get_city.value)

    def check_city(self, event):
        cities = self.personal_vk.method(
            "database.getCities", {"country_id": 1, 'q': event.message, "count": 1000}
        )["items"]

        for city in cities:
            if city["title"].lower() == event.message.lower():
                city_title: str = city["title"]
                self.orm.add_state(event.user_id, BotState.get_age.value)
                return city_title
            else:
                raise ValueError
        raise ValueError

    def get_age(self, event):
        self.write_msg(event.user_id, "Укажите возраст партнера:")

    def check_age(self, event):
        try:
            req_err = False
            if event.message.isdigit() is not True:
                self.write_msg(event.user_id, 'Проверьте возраст (должно быть целое число).')
                req_err = True
            if int(event.message) < 16:
                self.write_msg(event.user_id, 'Возрастные ограничения 16+.')
                req_err = True
            if req_err is False:
                return int(event.message)
            raise ValueError
        except ValueError:
            raise

    def confirm_all_data(self, event, data):
        user = self.orm.get_user(event.user_id)
        sex = user.gender
        if sex == 2:
            sex = 'девушку'
        else:
            sex = 'парня'
        self.write_msg(
            event.user_id,
            f"Ищем {sex} в возрасте {data['age']} из города {data['city'].capitalize()}",
            keyboard=empty_keyboard)
        self.search_users_info(event)

    def search_state(self, event):
        msg = event.message.lower()
        if msg == "показать избранных":
            self.show_favorite(event)

        elif msg == "показать заблокированных":
            self.write_msg(event.user_id, f'Список заблокированных вами пользователей❤')
            self.show_blacklist(event)

        elif msg == "подобрать":
            self.orm.clear_partner_all(self.orm.get_user_id(event.user_id))
            self.get_city(event)
            self.orm.add_state(event.user_id, BotState.get_city.value)
        elif msg == "автоподбор":
            print('auto')
            self.orm.clear_partner_all(self.orm.get_user_id(event.user_id))
            self.write_msg(event.user_id, 'Поиск будет выполнен на основе данных вашего профиля')
            search_data_info = self.orm.get_search_data(event.user_id)
            self.partner_age = search_data_info[0]
            self.partner_gender = search_data_info[1]
            self.hometown = search_data_info[2]
            self.next_partner(event, 25, self.partner_age, 0)
            self.write_msg(event.user_id, 'Пользователи найденные по вашему запросу',
                           keyboard=active_keyboard)
            self.partner_info = self.orm.get_random_partner()
            self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))

            self.orm.add_state(event.user_id, BotState.active_state.value)
        else:
            self.write_msg(event.user_id, "Не поняла вашего ответа... Можете повторить еще раз?")

    def search_users_info(self, event):
        request = event.text
        self.partner_age = int(request)
        print(self.partner_age)

        for age in range(self.partner_age - 1, self.partner_age + 2):
            start = datetime.datetime.now()
            self.next_partner(event, 100, age, 0)
            finish = datetime.datetime.now()
            print('Время работы: ' + str(finish - start))

        self.write_msg(event.user_id, 'Всё готово', keyboard=active_keyboard)
        self.partner_info = self.orm.get_random_partner()
        self.send_photos(event.user_id, ' '.join(self.partner_info[:3]), ','.join(self.partner_info[3]))
        self.orm.add_state(event.user_id, BotState.active_state.value)

    # def fourth_state(self, event, first_keyboard):
    #     request = event.text
    #     user_age = int(request)
    #     user_data = self.personal_vk.method(method='users.get',
    #                                         values={'user_ids': event.user_id, 'fields': 'sex,city,bdate'})
    #     self.orm.add_user(vk_id=event.user_id,
    #                       data={'age': user_age, 'city': user_data[0]['city']['title'],
    #                             'gender': user_data[0]['sex']})
    #     self.send_keyboard(event.user_id, 'Начинаем!', first_keyboard)
    #     self.current_state = 0
    #     self.orm.add_state(event.user_id, 0)

    def active_state(self, event):
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
            # self.orm.add_state(event.user_id, BotState.exit_state.value)
            self.end_discussion(event.user_id)

        elif request.lower() == 'в избранное':
            self.add_favorite(event)

        elif request.lower() == 'заблокировать':
            self.add_blacklist(event)

        elif request.lower() == 'лайк':
            self.personal_vk.method('likes.add',
                                    values={'type': 'photo', 'owner_id': '178546945', 'item_id': '457246150'})
