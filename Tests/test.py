from io import BytesIO

import pytest
import requests
from vk_api import upload


import main
from Repository import CardFavorites, CardExceptions
from main import handle_registration, User,send_message, save_anketa, upload_photo, add_favorites


class TestHandleRegistration:
    @pytest.fixture
    def user(self):
        return User(id_msg_edit_anketa=-1)

    def test_handle_registration(self, user, mocker):
        mocker.patch('main.vk_session.method')
        mocker.patch('main.ms.get_registration_massage', return_value="Registration message")

        result = handle_registration(user)
        assert result == "Registration message"


# class TestSendMessage:
#     """
#     В этом примере у нас есть два теста:
#      test_send_message_success, который проверяет успешную отправку сообщения,
#      и test_send_message_invalid_input,
#       который проверяет обработку недопустимого ввода.
#     """
#
#     def test_send_message_success(self, mocker):
#         message = {'user_id': 123, 'message': 'Test message'}
#         vk_session_mock = mocker.MagicMock()
#         mocker.patch('main.vk_session', vk_session_mock)
#
#         send_message(message)
#
#         vk_session_mock.method.assert_called_once_with('messages.send', message)
#
#     def test_send_message_invalid_input(self):
#         with pytest.raises(ValueError):
#             send_message({'user_id': 123})
#
#
# class TestSaveAnketa:
#     def test_save_anketa_success(self, mocker):
#         user = User(user_id=123, id_msg_edit_anketa=456)
#         repository_mock = mocker.MagicMock()
#         vk_session_mock = mocker.MagicMock()
#         ms_mock = mocker.MagicMock()
#         send_message_mock = mocker.MagicMock()
#         main_menu_mock = mocker.MagicMock()
#
#         mocker.patch('main.repository', repository_mock)
#         mocker.patch('main.vk_session', vk_session_mock)
#         mocker.patch('main.ms', ms_mock)
#         mocker.patch('main.send_message', send_message_mock)
#         mocker.patch('main.main_menu', main_menu_mock)
#
#         save_anketa(user)
#
#         repository_mock.add_user.assert_called_once_with(user)
#         vk_session_mock.method.assert_called_once_with('messages.delete', {
#             'message_ids': user.get_id_msg_edit_anketa(),
#             'delete_for_all': 1
#         })
#         assert user.get_id_msg_edit_anketa() == -1
#         ms_mock.get_message_done_registration.assert_called_once_with(user.get_user_id())
#         send_message_mock.assert_called_once()
#         main_menu_mock.assert_called_once_with(user)
#
#
# class TestUploadPhoto:
#     def test_upload_photo_success(self, mocker):
#         upload_mock = mocker.MagicMock()
#         url = 'https://example.com/photo.jpg'
#
#         response_data = {
#             'owner_id': 12345,
#             'id': 67890,
#             'access_key': 'abc123'
#         }
#
#         upload_mock.photo_messages.return_value = [response_data]
#
#         result = upload_photo(upload_mock, url)
#
#         upload_mock.photo_messages.assert_called_once()
#         f = BytesIO(requests.get(url).content)
#         upload_mock.photo_messages.assert_called_once_with(f)
#
#         assert result == response_data
#
#
# # Все  для функции view_next_card
# #-----------------------=======================
# class TestAddFavorites:
#     def test_add_favorites(mocker):
#         # Создать фиктивный объект репозитория
#         mock_repository = mocker.MagicMock()
#
#         #  Создать фиктивный объект пользователя
#         mock_user = mocker.MagicMock()
#
#         #  Вызвать функцию add_favorites с фиктивными объектами
#         add_favorites(mock_repository, mock_user)
#
#         # Утверждать, что метод add_favorites был вызван на фиктивном объекте репозитория один раз с фиктивным объектом пользователя
#         mock_repository.add_favorites.assert_called_once_with(mock_user)
#
#     def MagicMock(self):
#         pass
#
#
# class TestDeleteFromList:
#     def delete_from_list(user: User, repository):
#         if len(user.get_list_cards()) > 0:
#             if isinstance(user.get_list_cards()[0], CardFavorites):
#                 repository.delete_favorites(user.get_user_id(), user.get_card().profile)
#             elif isinstance(user.get_list_cards()[0], CardExceptions):
#                 repository.delete_exceptions(user.get_user_id(), user.get_card().profile)
#
#         user.delete_card()
#         main.view_next_card(upload, user, main.vk_srv, main.token)