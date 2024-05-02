
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
        self.__index_view = -1
        self.__list_cards = None
        self.__criteria = None

    def get_user_id(self):
        return self.__id

    def set_first_name(self, arg):
        self.__first_name = arg

    def get_first_name(self):
        return self.__first_name

    def set_last_name(self, arg):
        self.__last_name = arg

    def get_last_name(self):
        return self.__last_name

    def set_age(self, arg):
        self.__age = arg

    def get_age(self):
        return self.__age

    def set_gender(self, arg):
        self.__gender = arg

    def get_gender(self):
        return self.__gender

    def get_gender_str(self):
        return 'Женщина' if self.__gender == 1 else 'Мужчина'

    def set_city(self, arg):
        self.__city = arg

    def get_city(self):
        return self.__city

    def set_about_me(self, arg):
        self.__about_me = arg

    def get_about_me(self):
        return self.__about_me

    def set_id_msg_edit_anketa(self, arg):
        self.__id_msg_edit_anketa_id = arg

    def get_id_msg_edit_anketa(self):
        return self.__id_msg_edit_anketa_id

    def set_step(self, arg):
        self.__step = arg

    def get_step(self):
        return self.__step

    def set_index_view(self, arg):
        self.__index_view = arg

    def get_index_view(self):
        return self.__index_view

    def set_list_cards(self, arg):
        self.__list_cards = arg

    def get_list_cards(self):
        return self.__list_cards

    def get_card(self):
        return self.__list_cards[self.__index_view]

    def set_criteria(self, arg):
        self.__criteria = arg

    def get_criteria(self):
        return self.__criteria

    def delete_card(self):
        self.__list_cards.pop(self.__index_view)
        self.__index_view = self.__index_view - 1

    def get_size_list_cards(self):
        return len(self.__list_cards)

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