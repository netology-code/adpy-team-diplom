
class CardFind():
    def __init__(self, arg):
        self.id = arg['id']
        self.first_name = arg['first_name']
        self.last_name = arg['last_name']
        self.age = 0
        self.gender = arg['sex']
        self.profile = 'https://vk.com/id' + str(arg['id'])
        self.photos = None
        self.city_id = arg['city']['id']
        self.city_name = arg['city']['title']