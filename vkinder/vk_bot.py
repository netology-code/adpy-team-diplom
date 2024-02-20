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
        vk_group = vk_api.VkApi(token=group_token)
        vk_client = vk_api.VkApi(token=personal_token)
        self.long_poll = VkLongPoll(vk_group)
        self.vk_class = VkClass(vk_client, vk_group, orm, personal_token)

    def check_db(self):
        ORMvk.check_database(self.orm)

    def run_bot(self):
        self.check_db()

        first_keyboard = VkKeyboard()
        active_keyboard = VkKeyboard()

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
            for event in self.long_poll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        if self.orm.get_state(event.user_id) is not None:
                            self.vk_class.current_state = self.orm.get_state(event.user_id)
                        match self.vk_class.current_state:
                            case 0:
                                self.vk_class.check_user(event, first_keyboard, active_keyboard)
                            case 1:
                                self.vk_class.second_state(event)
                            case 2:
                                self.vk_class.third_state(event, active_keyboard)
                            case 3:
                                self.vk_class.active_state(event, first_keyboard)
                            case 4:
                                self.vk_class.fourth_state(event, first_keyboard)
        except Exception as e:
            print(e)
