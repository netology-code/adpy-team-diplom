from queue import Queue
from vk_bot.user import VkUserClient, StateEnum


class ActionEnum:
    PRESSED_NEXT_BUTTON: 0
    PRESSED_SHOW_FAVORITES: 0
    PRESSED_BLOCK_USER: 0
    PLAIN_TEXT: 0


class VkBot:
    def __init__(self):
        self.current_queues = {}

    def action(self, user_id, action_type: ActionEnum, message=""):
        user = VkUserClient(user_id)
        self.perform_user_action(user, action_type, message)

    def perform_user_action(self, user, action_type: ActionEnum, message):
        match action_type:
            case ActionEnum.PRESSED_NEXT_BUTTON:
                pass
            case ActionEnum.PRESSED_SHOW_FAVORITES:
                pass
            case ActionEnum.PRESSED_BLOCK_USER:
                pass
            case ActionEnum.PLAIN_TEXT:
                self.plain_text_action(user, message)

    def plain_text_action(self, user, message):
        match user.state:
            case StateEnum.REGISTERED:
                pass
            case StateEnum.ASK_AGE:
                pass
            case StateEnum.ASK_CITY:
                pass
            case StateEnum.ASK_GENDER:
                pass



