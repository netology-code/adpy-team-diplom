# функция получает информацию о потенциальном партнере через API
# НА ВХОД: список (token, age, gender, city)
# НА ВЫХОДЕ: список (partner_id, user_id, first_name, last_name, profile_ref, photo_ref1, photo_ref2, photo_ref3)

def get_partner_list_from_vk(user_info):
    # пример списка, который нужно вернуть в результаты выполнения функции
    partner_info = [
        [1001, 101, 'Маша', 'Иванова', 20, 'Female', 'vk.com/101', 'vk.com/1.jpg', 'vk.com/2.jpg', 'vk.com/3.jpg'],
        [1001, 102, 'Лена', 'Сидорова', 25, 'Female', 'vk.com/102', 'vk.com/1.jpg', 'vk.com/2.jpg', 'vk.com/3.jpg'],
        [1001, 103, 'Катя', 'Попова', 30, 'Female', 'vk.com/103', 'vk.com/1.jpg', 'vk.com/2.jpg', 'vk.com/3.jpg']
                    ]
    return partner_info