import pytest
from sqlalchemy.orm import sessionmaker
from CheckBD.CheckDBORM import CheckDBORM
from ORMTableStructure import Genders



class TestCheckDBORM:

    def setup_method(self):
        self.checkorm = CheckDBORM()

    def teardown_method(self):
        del self.checkorm

    @pytest.mark.parametrize('expected_bool',([True]))
    def test_exists_db(self, expected_bool):
        self.checkorm.create_db()
        actual_bool = self.checkorm.exists_db()
        assert actual_bool == expected_bool

    @pytest.mark.parametrize('expected_bool', ([True]))
    def test_exists_tables(self, expected_bool):
        self.checkorm.create_tables()
        actual_bool = self.checkorm.exists_tables()
        assert actual_bool == expected_bool

    @pytest.mark.parametrize('expected_count', ([2]))
    def test_fill_tables(self, expected_count):
        self.checkorm.fill_tables()
        Session = sessionmaker(bind=self.checkorm.get_engine())
        session = Session()
        actual_count = session.query(Genders).count()
        assert actual_count == expected_count