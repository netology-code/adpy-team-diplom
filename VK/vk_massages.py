from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from User import User
from search_criteria import create_search_criteria


def get_hello_massage(user_id, first_name):
    text_message = f'🚀 Привет, {first_name}!  👋  Я – бот, который экономит ' \
    f'твое время и помогает найти любовь быстро и легко! ' \
    f' ⏱️  Хочешь зарегистрироваться и начать поиск своей второй половинки?'

    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('хочу зарегистрироваться', color=VkKeyboardColor.POSITIVE)

    message = {
        'user_id': user_id,
        'message': text_message,
        'random_id': get_random_id(),
        'keyboard': keyboard.get_keyboard()
    }

    return message


# if __name__ == '__main__':
#     vk_reposiroty = VKRepository()
#     for event in VkLongPoll(session).listen():
#         if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
#             text = event.text.lower()
#             user_id = event.user_id
#             user_info = session.method('users.get', {'user_ids': user_id})[0]
#             first_name = user_info['first_name']
#             # first_name = vk_reposiroty.get_user_first_name(user_id)
#             keyboard = VkKeyboard(one_time=True)
#             keyboard.add_button('start', color=VkKeyboardColor.PRIMARY)
#             keyboard.add_button('хочу зарегистрироваться', color=VkKeyboardColor.POSITIVE)
#             if text == "start":
#                 keyboard = VkKeyboard(one_time=True)
#                 keyboard.add_button('Хочу зарегистрироваться', color=VkKeyboardColor.POSITIVE)
#                 send_message(user_id, f'🚀 Привет, {first_name}!  👋  Я – бот, который экономит '
#                                       f'твое время и помогает найти любовь быстро и легко! '
#                                       f' ⏱️  Хочешь зарегистрироваться и начать поиск своей второй половинки?  💖', keyboard)
#             if text == "хочу зарегистрироваться":
#                 keyboard = VkKeyboard(one_time=True)
#                 keyboard.add_button('Создание анкеты', color=VkKeyboardColor.POSITIVE)
#                 send_message(user_id, f'Здорово! 😊  Чтобы подобрать тебе идеальную пару, мне потребуется немного информации о твоих предпочтениях.'
#                                       f' 🔐  Не волнуйся, все данные останутся конфиденциальными. 😉', keyboard)
#
#             if text == "создание анкеты":
#                 keyboard = VkKeyboard(one_time=False)
#                 keyboard = VkKeyboard(one_time=False)
#                 keyboard = VkKeyboard(one_time=False)
#
#
#                 keyboard.add_button('Создать критерии', color=VkKeyboardColor.POSITIVE)
#                 keyboard.add_button('Поиск', color=VkKeyboardColor.POSITIVE)
#                 keyboard.add_line()
#                 keyboard.add_button('Изменить анкету', color=VkKeyboardColor.NEGATIVE)
#                 create_user_profile(user_id, session)
#                 send_message(user_id, 'Ура, твоя анкета создана! 🥳 \n\n'
#                                       'Можешь сразу начать поиск по умолчанию, который использует твой возраст и город, нажав "Поиск". \n\n'
#                                       'А если хочешь что-то особенное, нажми "Создать критерии" и мы найдём тебе идеальных кандидатов! 💥 \n'
#                                       'Кстати, ты всегда можешь изменить свою анкету в разделе "Изменить анкету".'
#                                       'Желаем тебе найти свою родственную душу! ❤️🌸   ', keyboard)
#
#                 if text == "Создать критерии":
#                     create_search_criteria(user_id, session)
#                     send_message(user_id, 'Критерии созданы! 👍 \n\n')
#
#                 elif text == "Поиск":
#                     assa = ''
#                     # users_list = vk_repository.get_users_list(criteria_dict)
#                     # вывод первого кандидата  фото имя фамилия возраст город
#                 elif text == "Изменить анкету":
#                     create_user_profile()
#                     send_message(user_id, 'Анкета изменена! 🥳 \n\n')
def get_hello_massage_error(user_id):
    text_message = f'🚀 Привет! ' \
                   f'Извините, сервис не доступен.' \
                   f'Попробуйте отправить сообщение позже.'

    message = {
        'user_id': user_id,
        'message': text_message,
        'random_id': get_random_id()
    }

    return message


def get_registration_massage(user: User):
    text_message = f'Анкета:\n' \
                   f'новое значение - нажать кнопку\n'
    settings = dict(one_time=False, inline=True)
    keyboard = VkKeyboard(**settings)
    keyboard.add_callback_button(label='Имя: '+user.get_first_name(), color=VkKeyboardColor.SECONDARY,
                                  payload={"action": "edit_first_name"})
    keyboard.add_line()
    keyboard.add_callback_button(label='Фамилия: '+user.get_last_name(), color=VkKeyboardColor.SECONDARY,
                                   payload={"action": "edit_last_name"})
    keyboard.add_line()
    keyboard.add_callback_button(label='Возраст: '+str(user.get_age()), color=VkKeyboardColor.SECONDARY,
                                   payload={"action": "edit_age"})
    keyboard.add_line()
    keyboard.add_callback_button(label='Город: '+user.get_city().get('title'), color=VkKeyboardColor.SECONDARY,
                                   payload={"action": "edit_city"})
    # keyboard.add_line()
    # keyboard.add_callback_button(label='Коротко обо мне: '+user.get_city().get('') + '\t', color=VkKeyboardColor.SECONDARY,
    #                                payload={"action": "edit_about_me"})

    message = {
        'user_id': user.get_user_id(),
        'message': text_message,
        'random_id': get_random_id(),
        'keyboard': keyboard.get_keyboard()
    }

    return message