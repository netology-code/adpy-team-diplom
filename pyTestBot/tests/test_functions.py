import pytest
from vk_users import get_user_info, search_possible_pair, get_photos


@pytest.mark.parametrize('user_id, result', [('238112071', True)])
def test_get_user_info(user_id, result):
    assert bool(get_user_info(user_id)) == result


@pytest.mark.parametrize('sex, age_from, age_to, city, count, result', [(1, 25, 30, 'Новосибирск', 10, True)])
def test_search_possible_pair(sex, age_from, age_to, city, count, result):
    assert bool(search_possible_pair(sex, age_from, age_to, city, count)) == result


@pytest.mark.parametrize('person_id, result', [('238112071', {323034194: 122, 456240736: 16, 457240781: 21})])
def test_get_photos(person_id, result):
    assert get_photos(person_id) == result
