class VKUser:
    url = ''
    photos_dict = {}
    relation = ''

    def __init__(self, id, name, surname, bdate, gender, city):
        self.id = id
        self.name = name
        self.surname = surname
        self.bdate = bdate
        self.gender = gender
        self.city = city