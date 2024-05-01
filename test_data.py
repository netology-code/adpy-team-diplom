from CheckBD.CheckDBORM import CheckDBORM
from Repository.ORMRepository import ORMRepository
from ORMTableStructure import get_class_cols
from ORMTableStructure import Cities, Genders

if __name__ == '__main__':

    test_db = CheckDBORM()
    test_db.create_db()
    test_db.create_tables()

    test_repo = ORMRepository()

    def add_city(city_list: list[dict]) -> None:
        # Выведение списка столбцов и их типов данных
        col_list, col_types_list = get_class_cols(Cities)
        for dict_city in city_list:
            # Проверка cоответствия ключей названию столбцов из col_list
            if test_repo.check_cols(col_list, dict_city):
                # Проверка cоответствия значений нужным типам данных
                if test_repo.check_columns_type(col_types_list, dict_city):
                    # Автоинкримент
                    dict_city = test_repo.do_autoincriment(dict_city, Cities)
                    # Запуск движка и инициация сессии
                    test_repo.start_add_table_session(dict_city, Cities)


    city_list = [
        {
            'id': 1,
            'name': 'Москва'
        },
        {
            'id': 2,
            'name': 'Самара'
        },
        {
            'id': 3,
            'name': 'Омск'
        }
    ]

    add_city(city_list=city_list)


    def add_genders(gender_list: list[dict]) -> None:
        # Выведение списка столбцов и их типов данных
        col_list, col_types_list = get_class_cols(Genders)
        for dict_gender in gender_list:
            # Проверка cоответствия ключей названию столбцов из col_list
            if test_repo.check_cols(col_list, dict_gender):
                # Проверка cоответствия значений нужным типам данных
                if test_repo.check_columns_type(col_types_list, dict_gender):
                    # Автоинкримент
                    dict_gender = test_repo.do_autoincriment(dict_gender, Genders)
                    # Запуск движка и инициация сессии
                    test_repo.start_add_table_session(dict_gender, Genders)


    gender_list = [
        {
            'id': 1,
            'gender': 'Женщина'
        },
        {
            'id': 2,
            'gender': 'Мужчина'
        },
        {
            'id': 3,
            'gender': 'Неизвестно'
        }
    ]

    add_genders(gender_list=gender_list)

    user_list = [
        {
            'id': 218879134,
            'first_name': 'Максим',
            'last_name': 'Терлецкий',
            'age': 28,
            'gender_id': 2,
            'city_id': 1,
            'about_me': 'Я из Москвы!'
        },
        {
            'id': 383309805,
            'first_name': 'Мария',
            'last_name': 'Алексеева',
            'age': 20,
            'gender_id': 1,
            'city_id': 2,
            'about_me': 'Я из Самары!'

        },
        {
            'id': 24661232,
            'first_name': 'Борис',
            'last_name': 'Казаков',
            'age': 48,
            'gender_id': 2,
            'city_id': 3,
            'about_me': 'Я из Омска!'
        }
    ]

    test_repo.add_user(user_list)

    favorites_list = [
        {
            'id': 1,
            'first_name': 'Анастасия',
            'last_name': 'Капибара',
            'user_id': 218879134,
            'age': 27,
            'gender_id': 1,
            'profile': 'KapibaraKing',
            'photo1': "https://sakhalinzoo.ru/upload/photos/650a793a66e3a_1695185210.jpg",
            'photo2': "https://www.zoo22.ru/upload/iblock/512/5121dc05f04d17658d18ecdc10687273.jpg",
            'photo3': "https://imgtest.mir24.tv/uploaded/images/crops/2022/October/870x489_0x132_detail_crop_20221005194604_4e816cd2_4caac5204c21955c3150533fdabf6489d1dc7f50d602bcb2a59650518f4b0bd8.jpg",
            'city_id': 1
        },
        {
            'id': 2,
            'first_name': 'Василиса',
            'last_name': 'Котовна',
            'user_id': 218879134,
            'age': 21,
            'gender_id': 1,
            'profile': 'HelloMeow',
            'photo1': "https://cdnn21.img.ria.ru/images/07e5/06/11/1737384810_0:123:2937:1775_1920x0_80_0_0_b3338c748c966d92967bd0af337fcd4b.jpg",
            'photo2': "https://irecommend.ru/sites/default/files/imagecache/copyright1/user-images/168296/E9XILUnWCLTbdCHMEYsg8w.JPG",
            'photo3': "https://mur-lamour.ru/wp-content/uploads/2017/07/british-shorthair3.jpg",
            'city_id': 2
        },
        {
            'id': 3,
            'first_name': 'Татьяна',
            'last_name': 'Хрюконовская',
            'user_id': 218879134,
            'age': 30,
            'gender_id': 1,
            'profile': 'HryuHryu',
            'photo1': "https://www.agroinvestor.ru/upload/iblock/9ff/9ff29da6f22b926ea7f7e27ae47a0a9e.jpg",
            'photo2': "https://cdn.fishki.net/upload/post/2018/02/13/2511394/tn/svinya-porosnok-zagorod-kopyta-krupnyy-plan-lico-78678-1920x1200.jpg",
            'photo3': "https://cdn.botanichka.ru/wp-content/uploads/2019/10/chem-kormit-sviney-05.jpg",
            'city_id': 3
        }
    ]

    test_repo.add_favorites(favorites_list)