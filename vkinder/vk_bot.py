import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from dotenv import load_dotenv, find_dotenv

from db.orm import ORMvk
from vkinder.vk_class import VkClass
from vkinder.vk_bot_state import BotState as Bs
from vkinder.vk_keyboard import create_first_keyboard, create_active_keyboard, create_empty_keyboard

load_dotenv(find_dotenv())

testers = None

first_keyboard = create_first_keyboard()
active_keyboard = create_active_keyboard()
empty_keyboard = create_empty_keyboard()


class VkBot:
    def __init__(self, orm, group_token, personal_token):
        self.orm = orm
        vk_group = vk_api.VkApi(token=group_token)
        vk_client = vk_api.VkApi(token=personal_token)
        self.long_poll = VkLongPoll(vk_group)
        self.vk_class = VkClass(vk_client, vk_group, orm, personal_token)

    def check_db(self):
        ORMvk.check_database(self.orm)

    def run_bot(self):
        self.check_db()

        users_requests = {'city': '', 'age': ''}
        while True:
            try:
                for event in self.long_poll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        actual_state = self.orm.get_state(event.user_id)

                        if not actual_state:
                            actual_state = Bs.empty_state.value

                        if actual_state == Bs.empty_state.value:
                            self.vk_class.check_user(event)

                        if actual_state == Bs.check_bdate.value:
                            self.vk_class.check_bdate(event.user_id, event.message)

                        if actual_state == Bs.main_state.value:
                            self.vk_class.main_state(event.user_id)

                        if actual_state == Bs.search_state.value:
                            self.vk_class.search_state(event)

                        if actual_state == Bs.get_city.value:
                            try:
                                self.vk_class.check_city(event)
                                city = event.message
                                users_requests['city'] = city
                                self.vk_class.get_age(event)
                                self.orm.add_state(event.user_id, Bs.get_age.value)
                            except ValueError:
                                self.vk_class.write_msg(event.user_id, 'К сожалению, я не могу определить город.'
                                                                       'Убедись, что в сообщении нет очпяток,'
                                                                       'и попробуем ещё раз.')
                                self.vk_class.get_city(event)

                        if actual_state == Bs.get_age.value:
                            try:
                                self.vk_class.check_age(event)
                                users_requests['age'] = event.message
                                self.orm.add_state(event.user_id, Bs.apply_search_params.value)

                                self.vk_class.confirm_all_data(event, users_requests)

                            except Exception:
                                ValueError("Ошибка проверки введенного запроса пользователя!")
                                self.vk_class.write_msg(event.user_id, 'Введите еще раз возраст партнера.')
                                self.orm.add_state(event.user_id, Bs.get_age.value)

                        if actual_state == Bs.apply_search_params.value:

                            self.vk_class.confirm_all_data(event, users_requests)

                        if actual_state == Bs.active_state.value:
                            self.vk_class.active_state(event)

            except Exception as e:
                print(e)
