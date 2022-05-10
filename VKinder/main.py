from db import add_to_favorites, add_new_user, user_authorized, get_user_info, display_favorites, add_partner_list_to_db
from vk import get_partner_list_from_vk

def main():

    token = input('Enter token to use the app: ')
    newUser = input('Enter n for a new user, any key for returning user')

    if newUser == 'n':
        # ввод информации о пользователе
        age = input('Enter age: ')
        gender = input('Enter gender: ')
        city = input('Enter city: ')
        # добавить нового пользователя в БД и вернуть user_id
        user_id = add_new_user(age, gender, city)
    else:
        user_id = int(input('Enter user_id: '))
        if not user_authorized(user_id):
            print('Access denied')
            # надо как-то закончить выполнение программы

    # получить данные пользователя из БД в виде словаря {'user_id': user_id, 'age': age, 'gender': gender, 'city': city}
    user_info = get_user_info(user_id)
    # получить список партнеров из ВК (список списков)
    partner_list = get_partner_list_from_vk(user_info)
    # добавить список партнеров в БД
    add_partner_list_to_db(partner_list)
    # достать список из БД
    partner_list = get_partner_list_from_db()

    # по партнерам из БД
    for partner in partner_list:
        # вывести в консоль доступные команды для управления ботом
        while True:
            print('n - first/next match\na - add to favorites\nd - display favorites\nPress any key to quit')
            user_cmd = input('Enter command: ')
            if user_cmd == 'n':
                # вывести в консоль информацию из БД о первом/следующем потенциальном партнере
                for item in partner:
                    print(item)
            elif user_cmd == 'a':
                add_to_favorites(partner[0], user_id)
            elif user_cmd == 'd':
                display_favorites(user_id)
            else:
                print('App finished')
                break

if __name__ == 'main':
    main()