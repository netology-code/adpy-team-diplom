Для создания БД запустите скрипт create_database.py (возможно потребуется дополнительная установка библиотек из файла requirements.txt)

Не забудьте заполнить файл setting.ini

Основные функции:
    
    add_favorite() - добавить кондидата в избранный лист(если кондидат находится
                     в чёрном списке через print можно вернуть предуприждение, 
                     внутри происходит авто проверка.
    
    add_blask() - аналогично add_favorite()

    get_all_favorite() - возвращает всех кондидатов находящихся в 
                         избранном списке 

    get_all_blask() - аналогично get_all_favorite()

    delete() - удаляет кандидата из списка(не имеет значение в каком он списке
               происходит каскадное удаление).
    


#пример 

    data = {'id': 111111, 'first_name': 'Ольга', 'last_name': 'Иванова', 'link': 'https://...', 'photos_ids': [1114524351, 11245351]}
    candidates = VKinderDB(data)

    candidates.add_favorite()
    #или вместе с print
    print(candidates.add_favorite())

    candidates.add_blask()
    #или вместе с print
    print(candidates.add_blask())

    #вернет список словарей
    #[{'id': ..., 'first_name': '...', 'last_name': '...', 'link': '...', 'photos_ids': [..., ...]}, {'id': ..., 'first_name': '...', 'last_name': '...', 'link': '...', 'photos_ids': [..., ...]}]
    print(candidates.get_all_favorite())

    #аналогично get_all_favorite()
    print(candidates.get_all_blask())
    
    #удаляет кандидата из списка
    candidates.delete()

