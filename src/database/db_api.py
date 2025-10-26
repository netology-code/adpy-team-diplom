#!/usr/bin/env python3
"""
API для интеграции с базой данных VKinder Bot
Предоставляет простые функции для использования в основном коде бота
"""

import sys
import os
from typing import Optional, List, Dict, Any
from .database_interface import DatabaseInterface
from .postgres_manager import PostgreSQLManager
from .models import VKUser, Photo, Favorite, Blacklisted, SearchHistory, UserSettings, BotLog, BotMessage
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
            from models import VKUser
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

def get_table_list() -> List[str]:
    """Получить список всех таблиц в базе данных"""
    try:
        from sqlalchemy import inspect
        db = DatabaseInterface()
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        return tables
    except Exception as e:
        logger.error(f"Ошибка получения списка таблиц: {e}")
        return []

def get_table_info(table_name: str) -> Dict[str, Any]:
    """Получить детальную информацию о таблице"""
    try:
        from sqlalchemy import inspect, text
        from datetime import datetime
        
        db = DatabaseInterface()
        inspector = inspect(db.engine)
        
        # Проверяем, существует ли таблица
        if table_name not in inspector.get_table_names():
            return None
        
        # Получаем количество записей
        with db.get_session() as session:
            count_result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = count_result.scalar()
        
        # Получаем размер таблицы
        with db.get_session() as session:
            size_result = session.execute(text(f"""
                SELECT pg_size_pretty(pg_total_relation_size('{table_name}')) as size
            """))
            size = size_result.scalar() or "N/A"
        
        # Получаем время последнего обновления (если есть поля updated_at или created_at)
        last_update = "N/A"
        try:
            with db.get_session() as session:
                # Сначала проверяем, какие поля времени существуют в таблице
                inspector = inspect(db.engine)
                columns = inspector.get_columns(table_name)
                column_names = [col['name'] for col in columns]
                
                # Проверяем наличие поля updated_at
                if 'updated_at' in column_names:
                    updated_result = session.execute(text(f"""
                        SELECT MAX(updated_at) FROM {table_name} 
                        WHERE updated_at IS NOT NULL
                    """))
                    updated_time = updated_result.scalar()
                    
                    if updated_time:
                        last_update = updated_time.strftime("%Y-%m-%d %H:%M:%S")
                elif 'created_at' in column_names:
                    # Если нет updated_at, проверяем created_at
                    created_result = session.execute(text(f"""
                        SELECT MAX(created_at) FROM {table_name} 
                        WHERE created_at IS NOT NULL
                    """))
                    created_time = created_result.scalar()
                    if created_time:
                        last_update = created_time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            # Если нет полей времени или ошибка, оставляем N/A
            logger.debug(f"Не удалось получить время обновления для таблицы {table_name}: {e}")
            pass
        
        return {
            'count': count,
            'size': size,
            'last_update': last_update
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения информации о таблице {table_name}: {e}")
        return None

def get_all_tables_info() -> Dict[str, Dict[str, Any]]:
    """Получить информацию о всех таблицах за один раз (оптимизированно)"""
    try:
        from sqlalchemy import inspect, text
        from datetime import datetime
        
        db = DatabaseInterface()
        inspector = inspect(db.engine)
        
        # Получаем список всех таблиц
        table_names = inspector.get_table_names()
        if not table_names:
            return {}
        
        # Собираем информацию о всех таблицах в одном подключении
        tables_info = {}
        
        with db.get_session() as session:
            # Получаем количество записей для всех таблиц одним запросом
            for table_name in table_names:
                try:
                    # Количество записей
                    count_result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = count_result.scalar()
                    
                    # Размер таблицы
                    size_result = session.execute(text(f"""
                        SELECT pg_size_pretty(pg_total_relation_size('{table_name}')) as size
                    """))
                    size = size_result.scalar() or "N/A"
                    
                    # Время последнего обновления
                    last_update = "N/A"
                    try:
                        # Проверяем поля времени
                        columns = inspector.get_columns(table_name)
                        column_names = [col['name'] for col in columns]
                        
                        if 'updated_at' in column_names:
                            updated_result = session.execute(text(f"""
                                SELECT MAX(updated_at) FROM {table_name} 
                                WHERE updated_at IS NOT NULL
                            """))
                            updated_time = updated_result.scalar()
                            if updated_time:
                                last_update = updated_time.strftime("%Y-%m-%d %H:%M:%S")
                        elif 'created_at' in column_names:
                            created_result = session.execute(text(f"""
                                SELECT MAX(created_at) FROM {table_name} 
                                WHERE created_at IS NOT NULL
                            """))
                            created_time = created_result.scalar()
                            if created_time:
                                last_update = created_time.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        pass  # Игнорируем ошибки с полями времени
                    
                    tables_info[table_name] = {
                        'count': count,
                        'size': size,
                        'last_update': last_update
                    }
                    
                except Exception as e:
                    logger.debug(f"Ошибка получения информации о таблице {table_name}: {e}")
                    tables_info[table_name] = {
                        'count': 'ERROR',
                        'size': 'ERROR',
                        'last_update': 'ERROR'
                    }
        
        return tables_info
        
    except Exception as e:
        logger.error(f"Ошибка получения информации о всех таблицах: {e}")
        return {}

def get_database_stats() -> Dict[str, Any]:
    """Получить статистику базы данных"""
    try:
        from sqlalchemy import inspect
        db = DatabaseInterface()
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        stats = {}
        stats['Таблицы'] = len(tables)
        
        # Подсчитываем записи в каждой таблице
        from sqlalchemy import text
        with db.get_session() as session:
            for table in tables:
                try:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    stats[f"Записей в {table}"] = count
                except Exception as e:
                    stats[f"Ошибка в {table}"] = str(e)
        
        return stats
    except Exception as e:
        logger.error(f"Ошибка получения статистики БД: {e}")
        return {"Ошибка": str(e)}

def create_all_tables() -> bool:
    """Создать все таблицы в базе данных"""
    try:
        db = DatabaseInterface()
        success = db.create_database()
        if success:
            logger.info("Все таблицы созданы успешно")
        else:
            logger.error("Ошибка создания таблиц")
        return success
    except Exception as e:
        logger.error(f"Ошибка создания таблиц: {e}")
        return False

def clear_all_tables() -> bool:
    """Очистить все таблицы в базе данных"""
    logger.info("🔍 Начинаем очистку всех таблиц...")
    
    try:
        logger.info("🔍 Создаем экземпляр DatabaseInterface...")
        db = DatabaseInterface()
        logger.info("✅ DatabaseInterface создан успешно")
        
        logger.info("🔍 Вызываем db.clear_all_tables()...")
        success = db.clear_all_tables()
        logger.info(f"📊 Результат db.clear_all_tables(): {success}")
        
        if success:
            logger.info("✅ Все таблицы очищены успешно")
        else:
            logger.error("❌ Ошибка очистки таблиц")
        return success
    except Exception as e:
        logger.error(f"❌ Ошибка очистки таблиц: {e}")
        logger.error(f"❌ Тип ошибки: {type(e).__name__}")
        logger.error(f"❌ Детали ошибки: {str(e)}")
        return False


# === УПРАВЛЕНИЕ ЧЕРНЫМ СПИСКОМ ===

def add_to_blacklist(user_id: int, blacklisted_id: int) -> bool:
    """
    Добавление пользователя в черный список
    
    Args:
        user_id: ID пользователя, который добавляет в черный список
        blacklisted_id: ID пользователя, которого добавляют в черный список
        
    Returns:
        bool: True если добавление успешно, False иначе
    """
    try:
        db = DatabaseInterface()
        if not db.test_connection():
            logger.error("❌ База данных недоступна")
            return False
        
        # Проверяем, есть ли уже в черном списке
        existing = db.get_blacklisted(user_id)
        if blacklisted_id in existing:
            logger.warning(f"⚠️ Пользователь {blacklisted_id} уже в черном списке пользователя {user_id}")
            return True
        
        # Добавляем в черный список
        success = db.add_to_blacklist(user_id, blacklisted_id)
        if success:
            logger.info(f"✅ Пользователь {blacklisted_id} добавлен в черный список пользователя {user_id}")
        else:
            logger.error(f"❌ Ошибка добавления пользователя {blacklisted_id} в черный список")
        return success
    except Exception as e:
        logger.error(f"❌ Ошибка добавления в черный список: {e}")
        return False


def get_blacklist(user_id: int) -> list:
    """
    Получение черного списка пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        list: Список ID пользователей в черном списке
    """
    try:
        db = DatabaseInterface()
        if not db.test_connection():
            logger.error("❌ База данных недоступна")
            return []
        
        blacklist = db.get_blacklisted(user_id)
        logger.info(f"✅ Получен черный список пользователя {user_id}: {len(blacklist)} пользователей")
        return blacklist
    except Exception as e:
        logger.error(f"❌ Ошибка получения черного списка: {e}")
        return []


def remove_from_blacklist(user_id: int, blacklisted_id: int) -> bool:
    """
    Удаление пользователя из черного списка
    
    Args:
        user_id: ID пользователя, который удаляет из черного списка
        blacklisted_id: ID пользователя, которого удаляют из черного списка
        
    Returns:
        bool: True если удаление успешно, False иначе
    """
    try:
        db = DatabaseInterface()
        if not db.test_connection():
            logger.error("❌ База данных недоступна")
            return False
        
        # Удаляем из черного списка
        success = db.remove_from_blacklist(user_id, blacklisted_id)
        if success:
            logger.info(f"✅ Пользователь {blacklisted_id} удален из черного списка пользователя {user_id}")
        else:
            logger.warning(f"⚠️ Пользователь {blacklisted_id} не найден в черном списке пользователя {user_id}")
        return success
    except Exception as e:
        logger.error(f"❌ Ошибка удаления из черного списка: {e}")
        return False


def is_user_blacklisted(user_id: int, target_user_id: int) -> bool:
    """
    Проверка, находится ли пользователь в черном списке
    
    Args:
        user_id: ID пользователя, чей черный список проверяется
        target_user_id: ID пользователя, которого проверяем
        
    Returns:
        bool: True если пользователь в черном списке, False иначе
    """
    try:
        db = DatabaseInterface()
        if not db.test_connection():
            logger.error("❌ База данных недоступна")
            return False
        
        blacklist = db.get_blacklisted(user_id)
        is_blacklisted = target_user_id in blacklist
        logger.debug(f"🔍 Проверка черного списка: пользователь {target_user_id} {'в' if is_blacklisted else 'не в'} черном списке пользователя {user_id}")
        return is_blacklisted
    except Exception as e:
        logger.error(f"❌ Ошибка проверки черного списка: {e}")
        return False


# === СТАТИСТИКА ПОЛЬЗОВАТЕЛЕЙ ===

def get_user_statistics(user_id: int) -> dict:
    """
    Получение статистики пользователя из базы данных
    
    Args:
        user_id: ID пользователя VK
        
    Returns:
        dict: Словарь со статистикой пользователя
    """
    try:
        db = DatabaseInterface()
        if not db.test_connection():
            logger.error("❌ База данных недоступна")
            return {}
        
        # Получаем статистику пользователя
        stats = db.get_user_statistics(user_id)
        logger.info(f"✅ Получена статистика пользователя {user_id}: {len(stats)} показателей")
        return stats
    except Exception as e:
        logger.error(f"❌ Ошибка получения статистики пользователя: {e}")
        return {}


def get_user_profile_stats(user_id: int) -> dict:
    """
    Получение расширенной статистики профиля пользователя
    
    Args:
        user_id: ID пользователя VK
        
    Returns:
        dict: Словарь с расширенной статистикой профиля
    """
    try:
        db = DatabaseInterface()
        if not db.test_connection():
            logger.error("❌ База данных недоступна")
            return {}
        
        # Получаем базовую статистику
        stats = db.get_user_statistics(user_id)
        
        # Добавляем дополнительную информацию о профиле
        with db.get_session() as session:
            # Количество поисковых запросов
            searches_count = session.query(SearchHistory).filter(
                SearchHistory.user_vk_id == user_id
            ).count()
            stats['total_searches'] = searches_count
            
            # Последний поиск
            last_search = session.query(SearchHistory).filter(
                SearchHistory.user_vk_id == user_id
            ).order_by(SearchHistory.created_at.desc()).first()
            
            if last_search:
                stats['last_search_date'] = last_search.created_at.isoformat()
                stats['last_search_results'] = last_search.results_count
            else:
                stats['last_search_date'] = None
                stats['last_search_results'] = 0
            
            # Настройки пользователя
            user_settings = session.query(UserSettings).filter(
                UserSettings.vk_user_id == user_id
            ).first()
            
            if user_settings:
                stats['user_settings'] = {
                    'min_age': user_settings.min_age,
                    'max_age': user_settings.max_age,
                    'sex_preference': user_settings.sex_preference,
                    'city_preference': user_settings.city_preference,
                    'online_only': user_settings.online
                }
            else:
                stats['user_settings'] = None
        
        logger.info(f"✅ Получена расширенная статистика профиля пользователя {user_id}")
        return stats
    except Exception as e:
        logger.error(f"❌ Ошибка получения статистики профиля: {e}")
        return {}


def get_user_activity_summary(user_id: int) -> dict:
    """
    Получение сводки активности пользователя
    
    Args:
        user_id: ID пользователя VK
        
    Returns:
        dict: Словарь со сводкой активности
    """
    try:
        db = DatabaseInterface()
        if not db.test_connection():
            logger.error("❌ База данных недоступна")
            return {}
        
        with db.get_session() as session:
            # Общая статистика активности
            activity = {}
            
            # Количество сообщений с ботом
            messages_count = session.query(BotMessage).filter(
                BotMessage.vk_user_id == user_id
            ).count()
            activity['messages_with_bot'] = messages_count
            
            # Количество логов пользователя
            logs_count = session.query(BotLog).filter(
                BotLog.vk_user_id == user_id
            ).count()
            activity['bot_logs_count'] = logs_count
            
            # Последняя активность
            last_message = session.query(BotMessage).filter(
                BotMessage.vk_user_id == user_id
            ).order_by(BotMessage.sent_at.desc()).first()
            
            if last_message:
                activity['last_activity'] = last_message.sent_at.isoformat()
            else:
                activity['last_activity'] = None
            
            # Статистика по дням (последние 7 дней)
            from datetime import datetime, timedelta
            week_ago = datetime.now() - timedelta(days=7)
            
            recent_searches = session.query(SearchHistory).filter(
                SearchHistory.user_vk_id == user_id,
                SearchHistory.created_at >= week_ago
            ).count()
            activity['searches_last_week'] = recent_searches
            
            recent_messages = session.query(BotMessage).filter(
                BotMessage.vk_user_id == user_id,
                BotMessage.sent_at >= week_ago
            ).count()
            activity['messages_last_week'] = recent_messages
        
        logger.info(f"✅ Получена сводка активности пользователя {user_id}")
        return activity
    except Exception as e:
        logger.error(f"❌ Ошибка получения сводки активности: {e}")
        return {}


if __name__ == "__main__":
    example_usage()
