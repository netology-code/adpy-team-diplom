Для создания БД запустите скрипт create_database.py (возможно потребуется дополнительная установка библиотек из файла requirements.txt)

Не забудьте заполнить файл setting.ini


#пример 

    peoples = Peoples()
    photos = Photos()
    favorite_people = Favorite()
    black_list = BlackList()

    # добавим нового человека.
    candidate = {
        'id_vk': 1, 'first_name': 'Grisha', 'last_name': 'Petrov',
        'age': 45, 'city': 'Москва', 'sex': 0
    }

    links = ['https://...', 'https://....', 'https://.....']

    # загрузим данные в БД
    peoples.insert(candidate)
    id_ = candidate.get('id_vk')
    # здесь берем именно id_vk так как он является уникальным в отличие от
    # имени и фамилии
    for link in links:
        photo = {'link': link, 'peoples_id': id_}
        photos.insert(photo)

    # добавим человека в избранный список для этого нужно получить id
    # если есть два человека с одинаковым именем и фамилией, тогда вернётся
    # список с id необходимо запросить у пользователя доп параметры.
    id_ = peoples.get_id('Grisha', 'Petrov')
    print(id_)
    favorite_people.insert(id_)

    # добавим человека в чёрный список.
    id_ = peoples.get_id('Grisha', 'Petrov')
    black_list.insert(id_)

    # поиск по имени
    pprint(peoples.search_name('Grisha', 'Petrov'))
    print()

    # выборка по возрасту
    pprint(peoples.search_age(21, 35))
    print()

    # выборка по городу
    pprint(peoples.search_city('SPB'))
    print()

    # выборка по полу
    pprint(peoples.search_sex(0))
    print()

    # удалить из избранного списка
    id_ = peoples.get_id('Grisha', 'Petrov')
    favorite_people.delete(id_)

    # удалить из чёрного списка
    id_ = peoples.get_id('Grisha', 'Petrov')
    black_list.delete(id_)

    # удалить из общего списка
    id_ = peoples.get_id('Grisha', 'Petrov')
    peoples.delete(id_)

    # получить всех пользоватлей
    pprint(peoples.get_all())

    # выборка по всем параметрам
    pprint(peoples.search_all_parameters(
        'Grisha', 'Petrov', 'Москва', 0, 18, 46
    ))
