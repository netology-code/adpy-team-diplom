from main import users_insert, pretendents_insert, favourites_insert,pretendents_output,favourites_output,vk_users_param_output
from pprint import pprint

if __name__ == '__main__':
##############################Вносим пользователей ВК################################
    # users_insert(123457222,  'Михайлов', 'Стас', 'Новгород', 25, 2)
    # users_insert(123457159, 'Семенов', 'Александр', 'Витебск', 30, 2)

###############################Вносим претендентов ################################
    # pretendents_insert(123457222, 159753759, 'Жмаева', 'Александра',
    #                    'https://vk.com/photo51800929_457257493',
    #                    'https://vk.com/photo51800929_457257493',
    #                    'https://vk.com/photo51800929_457257493' )
    #
    # pretendents_insert(123457222, 159753555, 'Клементьева', 'Марина',
    #                    'https://vk.com/photo51800929_457257493',
    #                    'https://vk.com/photo51800929_457257493',
    #                    'https://vk.com/photo51800929_457257493' )
    #
    # pretendents_insert(123457222, 1597535852, 'Семенова', 'Александра',
    #                    'https://vk.com/photo51800929_457257493',
    #                    'https://vk.com/photo51800929_457257493',
    #                    'https://vk.com/photo51800929_457257493' )
    #
    # pretendents_insert(123457159, 1597535777, 'Букина', 'Екатерина',
    #                    'https://vk.com/photo51800929_457257493',
    #                    'https://vk.com/photo51800929_457257493',
    #                    'https://vk.com/photo51800929_457257493' )
    #
    # pretendents_insert(123457159, 1597535895, 'Ростова', 'Наталья',
    #                    'https://vk.com/photo51800929_457257493',
    #                    'https://vk.com/photo51800929_457257493',
    #                    'https://vk.com/photo51800929_457257493' )


# ##############################Вносим избранных ################################
#     favourites_insert(123457222, 159753759, 'Жмаева', 'Александра',
#                         'https://vk.com/photo51800929_457257493',
#                         'https://vk.com/photo51800929_457257493',
#                         'https://vk.com/photo51800929_457257493')
#
#     favourites_insert(123457159, 1597535895, 'Ростова', 'Наталья',
#                        'https://vk.com/photo51800929_457257493',
#                        'https://vk.com/photo51800929_457257493',
#                        'https://vk.com/photo51800929_457257493')

#############################Вытаскиваем претендентов ################################
    pprint(pretendents_output(123457222))
    pprint(pretendents_output(123457159))
#
#
# ##############################Вытаскиваем избранных ################################
#     pprint(favourites_output(123457222))
#     pprint(favourites_output(123457159))



###############################Получаем город,пол,возраст пользователя вк ################################
    # pprint(vk_users_param_output(123457222))
    # pprint(vk_users_param_output(123457159))


