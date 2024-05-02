from User import User
from abc import ABC, abstractmethod


class ABCRepository(ABC):

    @abstractmethod
    def add_user(self, user: User):
        pass

    @abstractmethod
    def add_favorites(self, user_vk):
        pass

    @abstractmethod
    def add_exceptions(self, user_vk):
        pass

    @abstractmethod
    def delete_favorites(self, user_id, profile):
        pass

    @abstractmethod
    def delete_exceptions(self, user_id, profile):
        pass

    @abstractmethod
    def get_favorites(self, user_id):
        pass

    @abstractmethod
    def get_exceptions(self, user_id):
        pass

    @abstractmethod
    def get_user(self, user_id):
        pass

    @abstractmethod
    def open_criteria(self, user_id):
        pass
