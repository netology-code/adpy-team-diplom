
class User:
    def __init__(self, user_id):
        self.__id = user_id
        self.__first_name = ""
        self.__last_name = ""
        self.__age = 0
        self.__gender = 0
        self.__city = None
        self.__about_me = ""
        self.__id_msg_edit_anketa_id = -1
        self.__step = None

    def get_user_id(self):
        return self.__id

    def set_first_name(self, arg: str):
        self.__first_name = arg

    def get_first_name(self):
        return self.__first_name

    def set_last_name(self, arg: str):
        self.__last_name = arg

    def get_last_name(self):
        return self.__last_name

    def set_age(self, arg: int):
        self.__age = arg

    def get_age(self):
        return self.__age

    def set_gender(self, arg: int):
        self.__gender = arg

    def get_gender(self):
        return self.__gender

    def get_gender_str(self):
        return 'Женщина' if self.__gender == 1 else 'Мужчина'

    def set_city(self, arg: int):
        self.__city = arg

    def get_city(self) -> dict:
        return self.__city

    def set_about_name(self, arg: str):
        self.__about_me = arg

    def get_about_name(self):
        return self.__about_me

    def set_id_msg_edit_anketa(self, arg: int):
        self.__id_msg_edit_anketa_id = arg

    def get_id_msg_edit_anketa(self):
        return self.__id_msg_edit_anketa_id

    def set_step(self, arg: str):
        self.__step = arg

    def get_step(self):
        return self.__step

    def to_dict(self):
        return {
            'id': self.__id,
            'first_name': self.__first_name,
            'last_name': self.__last_name,
            'age': self.__age,
            'gender': self.__gender,
            'city': self.__city['id'],
            'about_me': self.__about_me
        }