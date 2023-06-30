from functools import total_ordering
from enum import Enum
from vk_bot.states.state import StateEnum
from database.requests import get_user_data, check_user_exits


class GenderEnum(Enum):
    MALE = 0
    FEMALE = 1


@total_ordering
class VkUser:
    def __init__(self, user_id: int):
        self.user_id = user_id

    def __lt__(self, other):
        return self.user_id < other.user_id

    def __eq__(self, other):
        return self.user_id == other.user_id

    def __hash__(self):
        return self.user_id


class VkUserClient(VkUser):
    def __init__(self, user_id):
        super().__init__(user_id)
        self.age = None
        self.city = None
        self.gender = None
        self.state = StateEnum.ASK_AGE
        self.try_get_data()

    def try_get_data(self):
        if check_user_exits(self.user_id):
            data = get_user_data(self.user_id)
            self.state = StateEnum(data.state)
            self.age = data.age
            self.city = data.city
            self.gender = GenderEnum(data.gender)

    def check_next_state(self):
        if self.state == StateEnum.REGISTERED:
            return
        elif self.age is None:
            self.state = StateEnum.ASK_AGE
        elif self.city is None:
            self.state = StateEnum.ASK_CITY
        elif self.gender is None:
            self.state = StateEnum.ASK_GENDER
        else:
            self.state = StateEnum.REGISTERED


class VkUserSearch(VkUser):
    def __init__(self, user_id):
        super().__init__(user_id)
        self.name = ""
        self.profile_link = f"https://vk.com/id{user_id}"
        self.photos = []
        self.related_photos = []
        self.interests = set
