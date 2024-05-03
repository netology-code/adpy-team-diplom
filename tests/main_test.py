import unittest
from io import BytesIO
from unittest import mock

from vk_api import upload

from Repository import CardFavorites, CardExceptions
from main import handle_start, handle_registration, ms, send_ask_edit_anketa, send_message, vk_srv, users_list, \
    send_message, set_param, save_anketa, main_menu, upload_photo, token
import requests
from main import find_users, view_next_card, view_back_card, check_user, handle_criteria, send_ask_edit_criteria, add_favorites, \
                  go_to_favorites, repository, delete_from_list, save_criteria


from User import User
from unittest.mock import patch, MagicMock, Mock

class TestHandleStart(unittest.TestCase):
    def setUp(self):
        # Инициализация данных для тестирования
        self.user_id = 123456
        self.users_list = {self.user_id: None}

    def test_handle_start_new_user(self):
        # Тест для случая, когда пользователь новый
        result = handle_start(self.user_id, self.users_list)
        self.assertIsNotNone(result)
        self.assertIn(self.user_id, self.users_list)

    def test_handle_start_existing_user(self):
        # Тест для случая, когда пользователь уже существует
        result = handle_start(self.user_id, self.users_list)
        self.assertIsNone(result)
        self.assertIn(self.user_id, self.users_list)

class TestHandleRegistration(unittest.TestCase):
    def setUp(self):
        self.user_id = 123456
        self.user = User(self.user_id)  # Создаем экземпляр User для тестирования
        self.users_list = {self.user_id: None}
    @patch('main.send_message')  # Мокаем функцию send_message
    def test_handle_registration(self, mock_send_message):
        # Вызываем функцию, которую хотим протестировать
        result = handle_registration(self.user)

        # Проверяем, что функция send_message была вызвана с правильным сообщением
        mock_send_message.assert_called_once_with(ms.get_registration_message(self.user)) # где ms - сообщение из модуля

        # Проверяем, что функция возвращает корректный ID сообщения
        self.assertIsNotNone(result)
        self.assertTrue(isinstance(result, int))

class TestSendAskEditAnketa(unittest.TestCase):
    @patch('vk_messages.User')
    @patch('main.ms')
    @patch('main.send_message')
    def test_send_ask_edit_anketa(self, mock_send_message, mock_ms, mock_user):
 # Создаем мок-объект User с заданными параметрами
        user = mock_user.return_value
        user.get_user_id.return_value = 123

        # Создаем мок-объект для ms.get_edit_message
        mock_ms.get_edit_message.return_value = 'Mocked edit message'

        # Аргументы для тестируемой функции
        str_arg = 'step1'

        # Вызываем тестируемую функцию
        send_ask_edit_anketa(user, str_arg)

        # Проверяем, что метод set_step был вызван с правильным аргументом
        user.set_step.assert_called_once_with('anketa_'+str_arg)

        # Проверяем, что ms.get_edit_message был вызван с правильными аргументами
        mock_ms.get_edit_message.assert_called_once_with(user.get_user_id(), str_arg)

        # Проверяем, что send_message был вызван с правильным сообщением
        mock_send_message.assert_called_once_with('Mocked edit message')


class TestSendMessage(unittest.TestCase):
    @patch('your_module.vk_session.method')
    def test_send_message(self, mock_method):
        # Создаем тестовый объект сообщения
        test_message = {
            'peer_id': 123456789,
            'message': f'🚀 Привет, {first_name}! 👋 Я – бот, который экономит твое время и помогает найти любовь быстро и легко!'
                       f' ⏱ Хочешь зарегистрироваться и начать поиск своей второй половинки?',
            'random_field': 'random_value'
        }

        # Вызываем функцию, которую хотим протестировать
        send_message(test_message)

        # Проверяем, что метод 'messages.send' был вызван с правильными аргументами
        mock_method.assert_called_once_with('messages.send', test_message)

        # Проверяем, что функция возвращает корректный ID сообщения
        self.assertIsNotNone(test_message.get('id'))
        self.assertTrue(isinstance(test_message.get('id'), int))
class TestSetParam(unittest.TestCase):

    @patch.object(User, 'get_step')
    @patch.object(User, 'set_first_name')
    def test_set_first_name(self, mock_set_first_name, mock_get_step):
        mock_get_step.return_value = 'anketa_first_name'
        user = User()
        set_param(user, 'John')
        mock_set_first_name.assert_called_once_with('John')

    @patch.object(User, 'get_step')
    @patch.object(User, 'set_last_name')
    def test_set_last_name(self, mock_set_last_name, mock_get_step):
        mock_get_step.return_value = 'anketa_last_name'
        user = User()
        set_param(user, 'Doe')
        mock_set_last_name.assert_called_once_with('Doe')

    @patch.object(User, 'get_step')
    @patch.object(User, 'set_age')
    def test_set_age(self, mock_set_age, mock_get_step):
        mock_get_step.return_value = 'anketa_age'

        user = User()
        set_param(user, '25')
        mock_set_age.assert_called_once_with('25')

    @patch.object(User, 'get_step')
    @patch.object(User, 'set_gender')
    def test_set_gender(self, mock_set_gender, mock_get_step):
        mock_get_step.return_value = 'anketa_gender'
        user = User()
        set_param(user, '1')
        mock_set_gender.assert_called_once_with(1)

    @patch.object(User, 'get_step')
    @patch.object(vk_srv, 'get_city_by_name')
    @patch.object(User, 'set_city')
    def test_set_city(self, mock_set_city, mock_get_city_by_name, mock_get_step):
        mock_get_step.return_value = 'anketa_city'
        mock_get_city_by_name.return_value = {'id': 1, 'name': 'Moscow'}
        user = User()
        set_param(user, 'Moscow')
        mock_set_city.assert_called_once_with({'id': 1, 'name': 'Moscow'})


class TestSaveAnketa(unittest.TestCase):
    @patch('your_module.repository')
    @patch('your_module.vk_session')
    def test_save_anketa(self, mock_vk_session, mock_repository):
        # Создаем мок-объект User
        user_mock = Mock(spec=User)
        user_mock.get_id_msg_edit_id.return_value = 12345

        # Определяем поведение мок-объекта repository.add_user
        mock_repository.add_user.return_value = None

        # Определяем поведение мок-объекта vk_session.method
        mock_vk_session.method.return_value = None

        # Вызываем функцию, которую тестируем
        save_anketa(user_mock)

        # Проверяем, что методы были вызваны с правильными аргументами
        mock_repository.add_user.assert_called_once_with(user_mock)
        mock_vk_session.method.assert_called_once_with('messages.delete', dict(message_ids=12345, delete_for_all=1))
        user_mock.set_id_msg_edit_id.assert_called_once_with(-1)

class TestMainMenuFunction(unittest.TestCase):
    @patch('User.User')
    @patch('vk_messages.ms.get_main_menu_message')
    @patch('main.send_message')
    def test_main_menu(self, mock_send_message, mock_get_main_menu_message, mock_user):
        # Создание моков для зависимостей
        mock_user.return_value = MagicMock()
        mock_get_main_menu_message.return_value = 'Mocked main menu message'

        # Вызов тестируемой функции
        main_menu(mock_user.return_value)

        # Проверка ожидаемых изменений в объекте User
        mock_user.return_value.set_list_cards.assert_called_once_with(None)
        mock_user.return_value.set_index_view.assert_called_once_with(-1)
        mock_user.return_value.set_id_msg_edit_id.assert_called_once_with(-1)

        # Проверка вызова функции get_main_menu_message
        mock_get_main_menu_message.assert_called_once_with(mock_user.return_value)

        # Проверка вызова функции send_message
        mock_send_message.assert_called_once_with('Mocked main menu message')

class TestUploadPhoto(unittest.TestCase):
    @mock.patch('requests.get')
    @mock.patch('vk_api.upload.VkUpload')
    def test_upload_photo(self, mock_upload, mock_get):
        # Определите ожидаемый URL и содержимое изображения
        expected_url = "http://example.com/image.jpg"
        expected_content = b"mocked image content"

        # Создаем мок-объект для upload.photo_messages
        mock_upload_response = {
            'owner_id': 123,
            'id': 456,
            'access_key': 'abc'
        }
        mock_upload.return_value.photo_messages.return_value = [mock_upload_response]

        # Установливаем поведение мок-объекта requests.get
        mock_get.return_value.content = expected_content

        # Вызываем функцию upload_photo с мок-объектами
        result = upload_photo(mock_upload, expected_url)

        # Проверяем, что функция вернула ожидаемые значения
        self.assertEqual(result, mock_upload_response)

        # Проверяем, что мок-объекты были вызваны с правильными аргументами
        mock_get.assert_called_once_with(expected_url)
        mock_upload.return_value.photo_messages.assert_called_once_with(BytesIO(expected_content))
class TestFindUsers(unittest.TestCase):
    @patch('your_module.vk_srv.users_search')
    def test_find_users(self, mock_users_search):
        # Создаем объект пользователя для тестирования
        user = User(123)

        # Устанавливаем возвращаемое значение для метода users_search
        mock_users_search.return_value = ['user1', 'user2']

        # Вызываем тестируемую функцию
        find_users(upload=MagicMock(), user=user, vk_srv=vk_srv, token='token')

        # Проверяем, что методы объекта пользователя были вызваны с правильными аргументами
        self.assertEqual(user.get_criteria(), ['user1', 'user2'])
        self.assertEqual(user.get_index_view(), -1)


class TestViewNextCard(unittest.TestCase):
    @patch('main.upload_photo')
    @patch('main.get_message_view')
    @patch('main.send_message')
    @patch('main.main_menu')
    def test_view_next_card(self, mock_main_menu, mock_send_message, mock_get_message_view, mock_upload_photo):
        # Создаем мок-объект для класса User
        mock_user = Mock(spec=User)
        mock_user.get_size_list_cards.return_value = 3
        mock_user.get_index_view.return_value = 0
        mock_user.set_index_view.return_value = None
        mock_user.get_list_cards.return_value = [Mock(), Mock(), Mock()]
        mock_user.get_card.return_value = 'card_info'

        # Моки для upload_photo
        mock_upload_photo.return_value = {'owner_id': 1, 'photo_id': 1, 'access_key': 1}

        # Моки для get_message_view
        mock_get_message_view.return_value = 'message_view'

        # Моки для send_message
        mock_send_message.return_value = None

        # Моки для main_menu
        mock_main_menu.return_value = None

        # Вызываем функцию с моками
        view_next_card(Mock(), mock_user, Mock(), Mock())

        # Проверяем, что моки были вызваны с правильными аргументами
        mock_user.get_size_list_cards.assert_called_once()
        mock_user.get_index_view.assert_called_once()
        mock_user.set_index_view.assert_called_once_with(1)
        mock_user.get_list_cards.assert_called_once()
        mock_user.get_card.assert_called_once()
        mock_upload_photo.assert_called_once()
        mock_get_message_view.assert_called_once_with(','.join(['photo1_1_1']), 'card_info', mock_user)
        mock_send_message.assert_called_once_with('message_view')
        mock_main_menu.assert_not_called()


class TestViewBackCard(unittest.TestCase):
    @patch('main.upload_photo')
    @patch('main.get_message_view')
    @patch('main.send_message')
    def test_view_back_card(self, mock_send_message, mock_get_message_view, mock_upload_photo):
        # Создаем мок-объект для класса User
        mock_user = Mock(spec=User)
        mock_user.get_index_view.return_value = 1
        mock_user.set_index_view.return_value = None
        mock_user.get_list_cards.return_value = [Mock(), Mock()]
        mock_user.get_card.return_value = 'card_info'

        # Моки для upload_photo
        mock_upload_photo.return_value = {'owner_id': 1, 'photo_id': 1, 'access_key': 1}

        # Моки для get_message_view
        mock_get_message_view.return_value = 'message_view'

        # Моки для send_message
        mock_send_message.return_value = None

        # Вызываем функцию с моками
        view_back_card(mock_user)

        # Проверяем, что моки были вызваны с правильными аргументами
        mock_user.get_index_view.assert_called_once()
        mock_user.set_index_view.assert_called_once_with(0)
        mock_user.get_list_cards.assert_called_once()
        mock_user.get_card.assert_called_once()
        mock_upload_photo.assert_called_once()
        mock_get_message_view.assert_called_once_with(','.join(['photo1_1_1']), 'info', mock_user)
        mock_send_message.assert_called_once_with('message_view')

class TestCheckUser(unittest.TestCase):
    @patch('main.repository.get_user')
    @patch('main.main_menu')
    @patch('main.send_message')
    def test_check_user(self, mock_send_message, mock_main_menu, mock_get_user):
        # Подготовка данных
        user_id = 12345
        mock_get_user.return_value = None

        # Выполнение функции
        user = check_user(user_id)

        # Проверка результатов
        mock_get_user.assert_called_once_with(user_id)
        mock_send_message.assert_called_once()
        mock_main_menu.assert_not_called()
        self.assertIsNone(user)  # Проверяем, что функция вернула None

        # Подготовка данных для другого сценария
        mock_get_user.return_value = MagicMock()
        mock_get_user.reset_mock()
        mock_send_message.reset_mock()
        mock_main_menu.reset_mock()

        # Выполнение функции
        user = check_user(user_id)

        # Проверка результатов
        mock_get_user.assert_called_once_with(user_id)
        mock_send_message.assert_not_called()
        mock_main_menu.assert_called_once_with(mock_get_user.return_value)
        self.assertIsInstance(user, MagicMock)  # Проверяем, что функция вернула объект User
class TestHandleCriteria(unittest.TestCase):
    @patch('main.repository.open_criteria')  # Замените на имя модуля, где находится функция repository.open_criteria
    @patch('main.ms.get_message_criteria')  # Замените на имя модуля, где находится функция ms.get_message_criteria
    @patch('main.send_message')
    @patch('main.vk_session.method')
    def test_handle_criteria(self, mock_vk_session_method, mock_send_message, mock_get_message_criteria, mock_open_criteria):
        # Подготовка данных
        user = MagicMock()
        user.get_criteria.return_value = None
        user.get_user_id.return_value = 123
        criteria_dict = {'key': 'value'}
        mock_open_criteria.return_value = criteria_dict

        # Выполнение тестируемой функции
        result = handle_criteria(user)

        # Проверка результатов
        self.assertIsNone(result)
        user.set_criteria.assert_called_once_with(criteria_dict)
        mock_get_message_criteria.assert_called_once_with(user)
        mock_send_message.assert_called_once_with(mock_get_message_criteria.return_value)
        mock_vk_session_method.assert_not_called()

        # Тест для случая, когда user.get_id_msg_edit_id() > -1
        user.get_id_msg_edit_id.return_value = 1
        result = handle_criteria(user)
        self.assertIsNone(result( mock_vk_session_method.assert_called_once_with('messages.delete', {'message_ids': 1, 'delete_for_all': 1})))

class TestSendAskEditCriteria(unittest.TestCase):
    @patch('main.ms')
    @patch('main.send_message')
    def test_send_ask_edit_criteria(self, mock_send_message, mock_ms):
        # Создаем мок-объект пользователя
        mock_user = MagicMock(spec=User)
        mock_user.get_user_id.return_value = 123456789
        mock_user.set_step.return_value = None

        # Устанавливаем ожидаемые значения для мок-методов
        mock_ms.get_edit_message.return_value = 'expected_message'

        # Вызываемруемую функцию
        send_ask_edit_criteria(mock_user, 'test_arg')

        # Проверяем, что методы были вызваны с правильными аргументами
        mock_user.set_step.assert_called_once_with('criteria_test_arg')
        mock_ms.get_edit_message.assert_called_once_with(123456789, 'test_arg')
        mock_send_message.assert_called_once_with('expected_message')

class TestAddFavorites(unittest.TestCase):
    def setUp(self):
        self.repository = Mock()  # Используем Mock для имитации репозитория
        self.user = User()  # Создаем пользователя для тестов

    def test_add_favorites(self):
        # Вызываем функцию, которую хотим протестировать
        add_favorites(self.repository, self.user)

        # Проверяем, что метод add_favorites был вызван с правильным аргументом
        self.repository.add_favorites.assert_called_once_with(self.user)

class TestGoToFavorites(unittest.TestCase):
    @patch('main.repository.get_favorites')
    @patch('main.set_list_cards')
    @patch('User.User.set_index_view')
    @patch('main.view_next_card')
    @patch('main.ms.get_message_error_search')
    @patch('main.send_message')
    def test_go_to_favorites(self, mock_send_message, mock_get_message_error_search, mock_view_next_card, mock_set_index_view, mock_set_list_cards, mock_get_favorites):
        # Создаем мок-объект для User
        user = Mock(spec=User)
        user.get_user_id.return_value= 123

        # Создаем мок-объекты для upload, vk_srv и token_api
        upload = Mock()
        vk_srv = Mock()
        token_api = Mock()

        # Устанавливаем поведение мок-функции get_favorites
        mock_get_favorites.return_value = ['card1', 'card2']

        # Вызываем функцию, которую хотим протестировать
        go_to_favorites(upload, user, repository, token_api)

        # Проверяем, что функции были вызваны с правильными аргументами
        mock_set_list_cards.assert_called_once_with(['card1', 'card2'])
        mock_set_index_view.assert_called_once_with(-1)
        mock_view_next_card.assert_called_once()

        # Устанавливаем поведение мок-функции get_favorites для случая, когда список карточек пуст
        mock_get_favorites.return_value = None

        # Вызываем функцию, которую хотим протестировать
        go_to_favorites(upload, user, repository, token_api)

        # Проверяем, что функции были вызваны с правильными аргументами
        mock_get_message_error_search.assert_called_once_with(user.get_user_id())
        mock_send_message.assert_called_once_with(mock_get_message_error_search.return_value)

class TestDeleteFromList(unittest.TestCase):
    '''
    В этом тесте мы используем моки для имитации поведения `User`, `repository`,
     `CardFavorites` и `CardExceptions`. Мы проверяем, что функция `delete_from_list` вызывает соответствующие методы
     `repository` для удаления из списка избранных или исключений, а также вызывает `view_next_card`
     после удаления карточки.
    '''
    def setUp(self):
        self.user = Mock(spec=User)
        self.repository = Mock(spec=repository)
        self.user.get_list_cards.return_value = [Mock(spec=CardFavorites), Mock(spec=CardExceptions)]
        self.user.get_card.return_value = Mock()
        self.user.delete_card.return_value = None

    @patch('main.view_next_card')
    def test_delete_from_list_favorites(self, mock_view_next_card):
        self.user.get_list_cards.return_value = [Mock(spec=CardFavorites)]
        delete_from_list(self.user, self.repository)
        self.repository.delete_favorites.assert_called_once_with(self.user.get_user_id(), self.user.get_card().profile)
        mock_view_next_card.assert_called_once_with(upload, self.user, vk_srv, token)

    @patch('main.view_next_card')
    def test_delete_from_list_exceptions(self, mock_view_next_card):
        self.user.get_list_cards.return_value = [Mock(spec=CardExceptions)]
        delete_from_list(self.user, self.repository)
        self.repository.delete_exceptions.assert_called_once_with(self.user.get_user_id(), self.user.get_card().profile)
        mock_view_next_card.assert_called_once_with(upload, self.user, vk_srv, token)

    def test_delete_from_list_empty_list(self):
        self.user.get_list_cards.return_value = []
        delete_from_list(self.user, self.repository)
        self.repository.delete_favorites.assert_not_called()
        self.repository.delete_exceptions.assert_not_called()

class TestSaveCriteria(unittest.TestCase):
    @patch('main.repository')
    @patch('main.users_list')
    @patch('main.vk_session')
    @patch('main.ms')
    @patch('main.send_message')
    @patch('main.main_menu')
    def test_save_criteria(self, mock_main_menu, mock_send_message, mock_ms, mock_vk_session, mock_users_list, mock_repository):
        # Создаем мок-объект пользователя
        user = MagicMock()
        user.get_user_id.return_value = 123
        user.get_id_msg_edit_id.return_value = 456
        users_list.__getitem__.return_value = user

        # Создаем мок-объект для message_id
        message_id = 789

        # Вызываем функцию, которую тестируем
        save_criteria(user)

        # Проверяем, что метод save_criteria был вызван с правильными аргументами
        mock_repository.save_criteria.assert_called_once_with(user)

        # Проверяем, что метод set_id_msg_edit_id был вызван у пользователя с правильным аргументом
        user.set_id_msg_edit_id.assert_called_once_with(message_id)

        # Проверяем, что метод messages.delete был вызван у vk_session с правильными аргументами
        mock_vk_session.method.assert_called_once_with(
            'messages.delete',
            dict(message_ids=456, delete_for_all=1)
        )

        # Проверяем, что метод get_message_done_registration был вызван у ms с правильным аргументом
        mock_ms.get_message_done_registration.assert_called_once_with(123)

        # Проверяем, что метод send_message был вызван с правильным аргументом
        mock_send_message.assert_called_once_with(mock_ms.get_message_done_registration.return_value)

        # Проверяем, что метод main_menu был вызван с правильным аргументом
        mock_main_menu.assert_called_once_with(user)

if __name__ == '__main__':
    unittest.main()