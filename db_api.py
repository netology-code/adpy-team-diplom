#!/usr/bin/env python3
"""
API для интеграции с базой данных VKinder Bot
Предоставляет простые функции для использования в основном коде бота
"""

import sys
import os
from typing import Optional, List, Dict, Any
from database_interface import DatabaseInterface
from postgres_manager import PostgreSQLManager
from loguru import logger

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Глобальный экземпляр интерфейса базы данных
_db_interface = None


def get_db_interface() -> DatabaseInterface:
    """
    Получение глобального экземпляра интерфейса базы данных
    
    Returns:
        DatabaseInterface: Экземпляр интерфейса БД
    """
    global _db_interface
    if _db_interface is None:
        _db_interface = DatabaseInterface()
    return _db_interface


# === УПРАВЛЕНИЕ БАЗОЙ ДАННЫХ ===

def create_database() -> bool:
    """
    Создание всех таблиц базы данных
    
    Returns:
        bool: True если создание успешно, False иначе
    """
    return get_db_interface().create_database()


def drop_database() -> bool:
    """
    Удаление всех таблиц базы данных
    
    Returns:
        bool: True если удаление успешно, False иначе
    """
    return get_db_interface().drop_database()


def clear_table(table_name: str) -> bool:
    """
    Очистка конкретной таблицы
    
    Args:
        table_name (str): Название таблицы для очистки
        
    Returns:
        bool: True если очистка успешна, False иначе
    """
    return get_db_interface().clear_table(table_name)


def clear_all_tables() -> bool:
    """
    Очистка всех таблиц (сохранение структуры)
    
    Returns:
        bool: True если очистка успешна, False иначе
    """
    return get_db_interface().clear_all_tables()


def get_database_info() -> Dict[str, Any]:
    """
    Получение информации о базе данных
    
    Returns:
        Dict[str, Any]: Словарь с информацией о таблицах
    """
    return get_db_interface().get_table_info()


# === УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ===

def add_user(vk_user_id: int, first_name: str, last_name: str, 
             age: Optional[int] = None, sex: Optional[int] = None,
             city: Optional[str] = None, country: Optional[str] = None,
             photo_url: Optional[str] = None) -> bool:
    """
    Добавление нового пользователя
    
    Args:
        vk_user_id (int): ID пользователя VK
        first_name (str): Имя
        last_name (str): Фамилия
        age (Optional[int]): Возраст
        sex (Optional[int]): Пол (1 - женский, 2 - мужской)
        city (Optional[str]): Город
        country (Optional[str]): Страна
        photo_url (Optional[str]): URL фотографии
        
    Returns:
        bool: True если добавление успешно, False иначе
    """
    result = get_db_interface().add_user(
        vk_user_id=vk_user_id,
        first_name=first_name,
        last_name=last_name,
        age=age,
        sex=sex,
        city=city,
        country=country,
        photo_url=photo_url
    )
    
    # Логируем вызов API функции
    if result:
        log_info(f"API: Пользователь {vk_user_id} ({first_name} {last_name}) добавлен через API")
    else:
        log_error(f"API: Ошибка добавления пользователя {vk_user_id} через API")
    
    return result


def get_user(vk_user_id: int) -> Optional[Dict[str, Any]]:
    """
    Получение пользователя по VK ID
    
    Args:
        vk_user_id (int): ID пользователя VK
        
    Returns:
        Optional[Dict[str, Any]]: Данные пользователя или None
    """
    try:
        db_interface = get_db_interface()
        with db_interface.get_session() as session:
            from src.database.models import VKUser
            user = session.query(VKUser).filter(VKUser.vk_user_id == vk_user_id).first()
            if user:
                return {
                    'id': user.id,
                    'vk_user_id': user.vk_user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'age': user.age,
                    'sex': user.sex,
                    'city': user.city,
                    'country': user.country,
                    'photo_url': user.photo_url,
                    'created_at': user.created_at,
                    'updated_at': user.updated_at
                }
        return None
    except Exception as e:
        logger.error(f"Ошибка получения пользователя {vk_user_id}: {e}")
        return None


def update_user(vk_user_id: int, **kwargs) -> bool:
    """
    Обновление данных пользователя
    
    Args:
        vk_user_id (int): ID пользователя VK
        **kwargs: Поля для обновления
        
    Returns:
        bool: True если обновление успешно, False иначе
    """
    result = get_db_interface().update_user(vk_user_id, **kwargs)
    
    # Логируем вызов API функции
    if result:
        log_info(f"API: Пользователь {vk_user_id} обновлен через API")
    else:
        log_error(f"API: Ошибка обновления пользователя {vk_user_id} через API")
    
    return result


def delete_user(vk_user_id: int) -> bool:
    """
    Удаление пользователя
    
    Args:
        vk_user_id (int): ID пользователя VK
        
    Returns:
        bool: True если удаление успешно, False иначе
    """
    result = get_db_interface().delete_user(vk_user_id)
    
    # Логируем вызов API функции
    if result:
        log_info(f"API: Пользователь {vk_user_id} удален через API")
    else:
        log_error(f"API: Ошибка удаления пользователя {vk_user_id} через API")
    
    return result


# === ЛОГИРОВАНИЕ ===

def log_info(message: str, user_id: int = 0) -> bool:
    """
    Запись информационного лога
    
    Args:
        message (str): Текст сообщения
        user_id (int): ID пользователя (0 для системных логов)
        
    Returns:
        bool: True если запись успешна, False иначе
    """
    return get_db_interface().add_bot_log(
        vk_user_id=user_id,
        log_level="info",
        log_message=message
    )


def log_debug(message: str, user_id: int = 0) -> bool:
    """
    Запись отладочного лога
    
    Args:
        message (str): Текст сообщения
        user_id (int): ID пользователя (0 для системных логов)
        
    Returns:
        bool: True если запись успешна, False иначе
    """
    return get_db_interface().add_bot_log(
        vk_user_id=user_id,
        log_level="debug",
        log_message=message
    )


def log_error(message: str, user_id: int = 0) -> bool:
    """
    Запись лога ошибки
    
    Args:
        message (str): Текст сообщения
        user_id (int): ID пользователя (0 для системных логов)
        
    Returns:
        bool: True если запись успешна, False иначе
    """
    return get_db_interface().add_bot_log(
        vk_user_id=user_id,
        log_level="error",
        log_message=message
    )


def log_warning(message: str, user_id: int = 0) -> bool:
    """
    Запись лога предупреждения
    
    Args:
        message (str): Текст сообщения
        user_id (int): ID пользователя (0 для системных логов)
        
    Returns:
        bool: True если запись успешна, False иначе
    """
    return get_db_interface().add_bot_log(
        vk_user_id=user_id,
        log_level="warning",
        log_message=message
    )


def get_logs(user_id: int = 0, level: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Получение логов
    
    Args:
        user_id (int): ID пользователя (0 для всех)
        level (Optional[str]): Уровень логирования
        limit (int): Максимальное количество записей
        
    Returns:
        List[Dict[str, Any]]: Список логов
    """
    return get_db_interface().get_bot_logs(
        vk_user_id=user_id,
        log_level=level,
        limit=limit
    )


# === СООБЩЕНИЯ ===

def add_message(user_id: int, message_type: str, message_text: str) -> bool:
    """
    Добавление сообщения бота
    
    Args:
        user_id (int): ID пользователя VK
        message_type (str): Тип сообщения (command, response, error)
        message_text (str): Текст сообщения
        
    Returns:
        bool: True если добавление успешно, False иначе
    """
    return get_db_interface().add_bot_message(
        vk_user_id=user_id,
        message_type=message_type,
        message_text=message_text
    )


def get_user_messages(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Получение сообщений пользователя
    
    Args:
        user_id (int): ID пользователя VK
        limit (int): Максимальное количество сообщений
        
    Returns:
        List[Dict[str, Any]]: Список сообщений
    """
    return get_db_interface().get_user_messages(
        vk_user_id=user_id,
        limit=limit
    )


# === ИЗБРАННОЕ ===

def add_favorite(user_id: int, favorite_id: int) -> bool:
    """
    Добавление в избранное
    
    Args:
        user_id (int): ID пользователя, который добавляет
        favorite_id (int): ID пользователя, которого добавляют
        
    Returns:
        bool: True если добавление успешно, False иначе
    """
    result = get_db_interface().add_favorite(
        user_vk_id=user_id,
        favorite_vk_id=favorite_id
    )
    
    # Логируем вызов API функции
    if result:
        log_info(f"API: Пользователь {favorite_id} добавлен в избранное к {user_id} через API")
    else:
        log_error(f"API: Ошибка добавления в избранное {favorite_id} к {user_id} через API")
    
    return result


def get_favorites(user_id: int) -> List[Dict[str, Any]]:
    """
    Получение списка избранных пользователя
    
    Args:
        user_id (int): ID пользователя VK
        
    Returns:
        List[Dict[str, Any]]: Список избранных
    """
    return get_db_interface().get_favorites(user_vk_id=user_id)


def remove_favorite(user_id: int, favorite_id: int) -> bool:
    """
    Удаление из избранного
    
    Args:
        user_id (int): ID пользователя
        favorite_id (int): ID пользователя для удаления
        
    Returns:
        bool: True если удаление успешно, False иначе
    """
    result = get_db_interface().remove_favorite(
        user_vk_id=user_id,
        favorite_vk_id=favorite_id
    )
    
    # Логируем вызов API функции
    if result:
        log_info(f"API: Пользователь {favorite_id} удален из избранного у {user_id} через API")
    else:
        log_error(f"API: Ошибка удаления из избранного {favorite_id} у {user_id} через API")
    
    return result


# === ТЕСТИРОВАНИЕ ===

def test_database() -> bool:
    """
    Тестирование подключения к базе данных
    
    Returns:
        bool: True если подключение работает, False иначе
    """
    return get_db_interface().test_connection()


def add_test_data() -> bool:
    """
    Добавление тестовых данных
    
    Returns:
        bool: True если добавление успешно, False иначе
    """
    try:
        # Добавляем тестового пользователя
        add_user(
            vk_user_id=999999,
            first_name="Тест",
            last_name="Пользователь",
            age=25,
            sex=2,
            city="Москва"
        )
        
        # Добавляем тестовые логи
        log_info("Тестовый лог от API", 999999)
        log_debug("Отладочный лог от API", 999999)
        
        # Добавляем тестовое сообщение
        add_message(999999, "command", "/test")
        add_message(999999, "response", "Тестовый ответ от API")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка добавления тестовых данных: {e}")
        return False


# === ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ===

def example_usage():
    """Примеры использования API"""
    
    print("🔧 Примеры использования API базы данных")
    print("=" * 50)
    
    # Тестирование подключения
    print("1. Тестирование подключения...")
    if test_database():
        print("✅ Подключение работает")
    else:
        print("❌ Ошибка подключения")
        return
    
    # Получение информации о БД
    print("\n2. Информация о базе данных...")
    info = get_database_info()
    print(f"📊 Всего таблиц: {info.get('total_tables', 0)}")
    
    # Добавление пользователя
    print("\n3. Добавление пользователя...")
    if add_user(123456, "Иван", "Петров", 30, 2, "СПб"):
        print("✅ Пользователь добавлен")
    else:
        print("❌ Ошибка добавления пользователя")
    
    # Логирование
    print("\n4. Логирование...")
    log_info("Пользователь зашел в бота", 123456)
    log_debug("Отладочная информация", 123456)
    logger.error("Тестовая ошибка", 123456)
    print("✅ Логи записаны")
    
    # Сообщения
    print("\n5. Сообщения...")
    add_message(123456, "command", "/start")
    add_message(123456, "response", "Привет! Добро пожаловать!")
    print("✅ Сообщения добавлены")
    
    # Избранное
    print("\n6. Избранное...")
    # Сначала добавляем пользователя, которого будем добавлять в избранное
    add_user(789012, "Анна", "Смирнова", 28, 1, "Москва")
    add_favorite(123456, 789012)
    print("✅ Добавлено в избранное")
    
    # Получение данных
    print("\n7. Получение данных...")
    user = get_user(123456)
    if user:
        print(f"✅ Пользователь найден: {user['first_name']} {user['last_name']}")
    
    messages = get_user_messages(123456, limit=5)
    print(f"✅ Найдено сообщений: {len(messages)}")
    
    logs = get_logs(user_id=123456, limit=5)
    print(f"✅ Найдено логов: {len(logs)}")
    
    favorites = get_favorites(123456)
    print(f"✅ Найдено избранных: {len(favorites)}")
    
    print("\n✅ Все примеры выполнены успешно!")


# === УПРАВЛЕНИЕ POSTGRESQL ===

def start_postgresql() -> bool:
    """
    Запуск PostgreSQL (универсальный для всех ОС)
    
    Returns:
        bool: True если запуск успешен, False иначе
    """
    try:
        manager = PostgreSQLManager()
        result = manager.start_postgresql()
        
        if result:
            log_info("PostgreSQL запущен через API")
        else:
            log_error("Ошибка запуска PostgreSQL через API")
        
        return result
    except Exception as e:
        log_error(f"Ошибка запуска PostgreSQL: {e}")
        return False


def stop_postgresql() -> bool:
    """
    Остановка PostgreSQL (универсальный для всех ОС)
    
    Returns:
        bool: True если остановка успешна, False иначе
    """
    try:
        manager = PostgreSQLManager()
        result = manager.stop_postgresql()
        
        if result:
            log_info("PostgreSQL остановлен через API")
        else:
            log_error("Ошибка остановки PostgreSQL через API")
        
        return result
    except Exception as e:
        log_error(f"Ошибка остановки PostgreSQL: {e}")
        return False


def restart_postgresql() -> bool:
    """
    Перезапуск PostgreSQL (универсальный для всех ОС)
    
    Returns:
        bool: True если перезапуск успешен, False иначе
    """
    try:
        manager = PostgreSQLManager()
        result = manager.restart_postgresql()
        
        if result:
            log_info("PostgreSQL перезапущен через API")
        else:
            log_error("Ошибка перезапуска PostgreSQL через API")
        
        return result
    except Exception as e:
        log_error(f"Ошибка перезапуска PostgreSQL: {e}")
        return False


def check_postgresql_status() -> bool:
    """
    Проверка статуса PostgreSQL
    
    Returns:
        bool: True если PostgreSQL запущен, False иначе
    """
    try:
        manager = PostgreSQLManager()
        result = manager.check_postgresql_status()
        
        if result:
            log_info("PostgreSQL статус: запущен")
        else:
            log_warning("PostgreSQL статус: не запущен")
        
        return result
    except Exception as e:
        log_error(f"Ошибка проверки статуса PostgreSQL: {e}")
        return False


def get_postgresql_info() -> Dict[str, Any]:
    """
    Получение информации о PostgreSQL
    
    Returns:
        Dict[str, Any]: Информация о PostgreSQL
    """
    try:
        manager = PostgreSQLManager()
        info = manager.get_postgresql_info()
        
        if 'error' not in info:
            log_info("Информация о PostgreSQL получена через API")
        else:
            log_error(f"Ошибка получения информации о PostgreSQL: {info['error']}")
        
        return info
    except Exception as e:
        log_error(f"Ошибка получения информации о PostgreSQL: {e}")
        return {'error': str(e)}


def create_database_if_not_exists() -> bool:
    """
    Создание базы данных если она не существует
    
    Returns:
        bool: True если БД создана или существует, False иначе
    """
    try:
        manager = PostgreSQLManager()
        result = manager.create_database_if_not_exists()
        
        if result:
            log_info("База данных создана или уже существует через API")
        else:
            log_error("Ошибка создания базы данных через API")
        
        return result
    except Exception as e:
        log_error(f"Ошибка создания базы данных: {e}")
        return False


def ensure_postgresql_ready() -> bool:
    """
    Гарантирует, что PostgreSQL готов к работе
    
    Returns:
        bool: True если PostgreSQL готов, False иначе
    """
    try:
        log_info("Проверка готовности PostgreSQL через API")
        
        manager = PostgreSQLManager()
        
        # Проверяем и запускаем PostgreSQL
        if not manager.ensure_postgresql_running():
            log_error("Не удалось запустить PostgreSQL через API")
            return False
        
        # Создаем БД если нужно
        if not manager.create_database_if_not_exists():
            log_error("Не удалось создать базу данных через API")
            return False
        
        log_info("PostgreSQL готов к работе через API")
        return True
        
    except Exception as e:
        log_error(f"Ошибка подготовки PostgreSQL: {e}")
        return False


# === ДОПОЛНИТЕЛЬНЫЕ ИМПОРТЫ ===
import subprocess
import time


if __name__ == "__main__":
    example_usage()
