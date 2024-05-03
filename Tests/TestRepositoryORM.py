import pytest
from sqlalchemy.orm import sessionmaker

from User import User
from CheckBD.ORMTableStructure import Users
from Repository.ORMRepository import ORMRepository


expected_result = {'_User__id': 10101010, '_User__first_name': 'Тестовый', '_User__last_name': 'Пользователь', '_User__age': 28, '_User__gender': 2,'_User__city': {'id': 1, 'title': 'Москва'},'_User__about_me': 'Я тестовый пользователь', '_User__id_msg_edit_anketa_id': -1,'_User__step': None, '_User__index_view': -1, '_User__list_cards': None, '_User__criteria': {'id': 3, 'gender_id': 1, 'status': 1, 'age_from': 23, 'age_to': 33, 'city': {'id': 1, 'name': 'Москва'}, 'has_photo': 1}}



class TestRepositoryORM:

    def setup_method(self):
        self.checkorm = ORMRepository()
        self.user = User(10101010)

    def teardown_method(self):
        del self.checkorm
        del self.user

    @pytest.mark.parametrize('expected_result',([expected_result]))
    def test_add_user(self, expected_result):

        self.user.set_first_name('Тестовый')
        self.user.set_last_name('Пользователь')
        self.user.set_age(28)
        self.user.set_gender(2)
        self.user.set_gender(2)
        self.user.set_city({'id': 1, 'title': 'Москва'})
        self.user.set_about_me("Я тестовый пользователь")

        self.checkorm.add_user(self.user)
        actual_result = self.checkorm.get_user(10101010)

        assert actual_result == expected_result

        engine = self.checkorm.get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        user_to_delete = session.query(Users).\
            filter_by(user_id=10101010).\
            first()

        session.delete(user_to_delete)
        session.commit()
        session.close()