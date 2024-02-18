from datetime import date

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from dotenv import load_dotenv, find_dotenv

from db.orm import ORMvk
from vkinder.vk_class import VkClass

load_dotenv(find_dotenv())

testers = None


class VkBot:
    def __init__(self, orm, group_token, personal_token):
        self.orm = orm
        self.group_token = group_token
        self.personal_token = personal_token

    def check_db(self):
        ORMvk.check_database(self.orm)

    def create_vk_group(self):
        return vk_api.VkApi(token=self.group_token)

    def create_vk_personal(self):
        return vk_api.VkApi(token=self.personal_token)

    def create_vkbot(self):
        return VkClass(self.create_vk_personal(), self.create_vk_group(), self.orm, self.personal_token)

    def run_bot(self):
        self.check_db()

        first_keyboard = VkKeyboard()
        active_keyboard = VkKeyboard()
        longpoll = VkLongPoll(self.create_vk_group())
        vkbot = self.create_vkbot()

        first_keyboard.add_button('Подобрать', VkKeyboardColor.PRIMARY)
        first_keyboard.add_button('Автоподбор', VkKeyboardColor.PRIMARY)
        first_keyboard.add_line()
        first_keyboard.add_button('Показать избранных', VkKeyboardColor.PRIMARY)
        first_keyboard.add_button('Показать заблокированных', VkKeyboardColor.PRIMARY)

        active_keyboard.add_button('Следующий', VkKeyboardColor.PRIMARY)
        active_keyboard.add_button('Выйти', VkKeyboardColor.PRIMARY)
        active_keyboard.add_line()
        active_keyboard.add_button('В избранное', VkKeyboardColor.PRIMARY)
        active_keyboard.add_button('Заблокировать', VkKeyboardColor.PRIMARY)
        active_keyboard.add_line()
        active_keyboard.add_button('Лайк', VkKeyboardColor.PRIMARY)
        active_keyboard.add_button('Дизлайк', VkKeyboardColor.PRIMARY)
        try:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        if self.orm.get_state(event.user_id) is not None:
                            vkbot.current_state = self.orm.get_state(event.user_id)
                        match vkbot.current_state:
                            case 0:
                                if self.orm.get_user_id(event.user_id) is None:
                                    user_data = vkbot.personal_vk.method(method='users.get',
                                                                         values={'user_ids': event.user_id,
                                                                                 'fields': 'sex,city,bdate'})
                                    if 'bdate' in user_data[0].keys():
                                        if len(user_data[0]['bdate']) > 8:
                                            user_age = int(str(date.today())[:4]) - int(user_data[0]['bdate'][-4:])
                                            self.orm.add_user(vk_id=event.user_id,
                                                              data={'age': user_age, 'city': user_data[0]['city']['title'],
                                                                    'gender': user_data[0]['sex']})
                                            vkbot.first_state(event, first_keyboard, active_keyboard)
                                        else:
                                            vkbot.write_msg(event.user_id, "Введите ваш возраст")
                                            vkbot.current_state = 4
                                            vkbot.orm.add_state(event.user_id, 4)
                                    else:
                                        vkbot.write_msg(event.user_id, "Введите ваш возраст")
                                        vkbot.current_state = 4
                                        vkbot.orm.add_state(event.user_id, 4)
                                else:
                                    vkbot.first_state(event, first_keyboard, active_keyboard)
                            case 1:
                                vkbot.second_state(event)
                            case 2:
                                vkbot.third_state(event, active_keyboard)
                            case 3:
                                vkbot.active_state(event, first_keyboard)
                            case 4:
                                vkbot.fourth_state(event, first_keyboard)
        except Exception as e:
            print(e)
