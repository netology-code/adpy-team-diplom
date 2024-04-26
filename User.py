
class User:
    def __init__(self):
        self.first_name = ""
        self.last_name = ""
        self.age = 0
        self.gender = 0
        self.city = 0
        self.about_name = ""

    def set_first_name(self, arg: str):
        self.first_name = arg

    def set_last_name(self, arg: str):
        self.last_name = arg

    def set_age(self, arg: int):
        self.age = arg

    def set_gender(self, arg: int):
        self.gender = arg

    def set_city(self, arg: int):
        self.city = arg

    def set_about_name(self, arg: int):
        self.about_name = arg