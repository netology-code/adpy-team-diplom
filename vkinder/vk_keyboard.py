import json

from vk_api.keyboard import VkKeyboard, VkKeyboardColor


# keyboard = VkKeyboard()

def create_first_keyboard():
    keyboard = VkKeyboard()

    keyboard.add_button('Подобрать', VkKeyboardColor.PRIMARY)
    keyboard.add_button('Автоподбор', VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Показать избранных', VkKeyboardColor.PRIMARY)
    keyboard.add_button('Показать заблокированных', VkKeyboardColor.PRIMARY)

    return keyboard.get_keyboard()


def create_active_keyboard():
    keyboard = VkKeyboard()
    keyboard.add_button('Следующий', VkKeyboardColor.PRIMARY)
    keyboard.add_button('Выйти', VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('В избранное', VkKeyboardColor.PRIMARY)
    keyboard.add_button('Заблокировать', VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('Лайк', VkKeyboardColor.PRIMARY)
    keyboard.add_button('Дизлайк', VkKeyboardColor.PRIMARY)
    return keyboard.get_keyboard()


def create_empty_keyboard():
    keyboard = VkKeyboard()
    keyboard = keyboard.get_empty_keyboard()

    return json.dumps(keyboard)

# def empty_keyboard():
#     return {'keyboard': {"one_time": False, "buttons": []}}
