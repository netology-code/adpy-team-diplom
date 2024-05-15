from abc import ABC, abstractmethod


class ABCCheckDb(ABC):
    def __init__(self):
        self.error = None
        self.connect = None
        self.db_name = 'findme'
        self.tables = ['criteria', 'genders', 'cities', 'users', 'favorites', 'exceptions']

    def check_db(self) -> bool:
        """
        Проверка, есть база данных или нет
        Если нет - создадим
        """
        self.create_db()
        self.create_tables()
        self.fill_tables()

        return self.error is None

    @abstractmethod
    def exists_db(self) -> bool:
        """
        Проверка, есть база данных или нет
        Returns:
            bool : True - есть база данных, False - нет базы данных
        """
        pass

    @abstractmethod
    def create_db(self):
        """
        Создание базы данных
        """
        if not self.exists_db():
            pass

    @abstractmethod
    def exists_tables(self, name_table) -> bool:
        """
        Проверка, все ли нужные таблицы созданы
        Returns:
            bool : True - если созданы, False - нет
        """
        pass

    @abstractmethod
    def create_tables(self):
        """
        Создание таблиц
        """

        if not self.error is None:
            return

        # Проверим наличие всех нужных тамблиц
        for name_table in self.tables:
            if not self.exists_tables(name_table):
                self.error = 'Не все таблицы созданы'

    @abstractmethod
    def fill_tables(self) -> bool:
        """
        Заполнение предопределенными данными
        После заполнения self.is_all_right нужно установить True
        """
        pass
