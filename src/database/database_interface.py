#!/usr/bin/env python3
"""
Интерфейс для работы с базой данных VKinder Bot
Предоставляет полный набор функций для управления БД, записи данных и обработки исключений
"""

import sys
import os
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from contextlib import contextmanager

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Исправляем импорты для работы как отдельного скрипта
try:
    from .models import (
        Base, VKUser, Photo, Favorite, Blacklisted, SearchHistory, 
        UserSettings, BotLog, BotMessage
    )
except ImportError:
    # Если относительные импорты не работают, используем абсолютные
    from models import (
        Base, VKUser, Photo, Favorite, Blacklisted, SearchHistory, 
        UserSettings, BotLog, BotMessage
    )
import os
from dotenv import load_dotenv
from loguru import logger
try:
    from .postgres_manager import PostgreSQLManager
except ImportError:
    from postgres_manager import PostgreSQLManager

# Загружаем переменные окружения
load_dotenv()


class DatabaseInterface:
    """
    Полноценный интерфейс для работы с базой данных VKinder Bot
    
    Предоставляет функции для:
    - Создания/удаления/очистки базы данных
    - Управления таблицами
    - CRUD операций с данными
    - Обработки исключений
    - Логирования операций
    """
    
    def __init__(self):
        """Инициализация интерфейса базы данных"""
        self.engine = None
        self.Session = None
        self._setup_connection()
    
    def _setup_connection(self):
        """Настройка подключения к базе данных"""
        try:
            # Проверяем и запускаем PostgreSQL если нужно
            postgres_manager = PostgreSQLManager()
            if not postgres_manager.ensure_postgresql_running():
                logger.error("❌ Не удалось запустить PostgreSQL")
                raise Exception("PostgreSQL недоступен")
            
            # Создаем БД если не существует
            if not postgres_manager.create_database_if_not_exists():
                logger.error("❌ Не удалось создать базу данных")
                raise Exception("База данных недоступна")
            
            # Создаем подключение к PostgreSQL
            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = os.getenv('DB_PORT', '5432')
            db_name = os.getenv('DB_NAME', 'vkinder_db')
            db_user = os.getenv('DB_USER', 'vkinder_user')
            db_password = os.getenv('DB_PASSWORD', 'vkinder123')
            
            database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            self.engine = create_engine(database_url, echo=False)
            self.Session = sessionmaker(bind=self.engine)
            
            logger.info("✅ Интерфейс базы данных инициализирован с автоматическим запуском PostgreSQL")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации интерфейса БД: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Контекстный менеджер для работы с сессией БД"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка в сессии БД: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """
        Тестирование подключения к базе данных
        
        Returns:
            bool: True если подключение успешно, False иначе
        """
        try:
            with self.get_session() as session:
                # Простой запрос для проверки подключения
                result = session.execute(text("SELECT 1")).fetchone()
                logger.info("✅ Подключение к базе данных работает")
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к БД: {e}")
            return False
    
    def create_database(self) -> bool:
        """
        Создание всех таблиц базы данных
        
        Returns:
            bool: True если создание успешно, False иначе
        """
        try:
            logger.info("🔨 Создание таблиц базы данных...")
            Base.metadata.create_all(self.engine)
            logger.info("✅ Все таблицы созданы успешно")
            
            # Логируем действие в БД
            self.add_bot_log(
                vk_user_id=0,  # Системный лог
                log_level="info",
                log_message="Все таблицы базы данных созданы"
            )
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания таблиц: {e}")
            return False
    
    def drop_database(self) -> bool:
        """
        Удаление всех таблиц базы данных
        
        Returns:
            bool: True если удаление успешно, False иначе
        """
        try:
            logger.info("🗑️ Удаление всех таблиц...")
            Base.metadata.drop_all(self.engine)
            logger.info("✅ Все таблицы удалены")
            
            # Логируем действие в БД (если таблица bot_logs еще существует)
            try:
                self.add_bot_log(
                    vk_user_id=0,  # Системный лог
                    log_level="warning",
                    log_message="Все таблицы базы данных удалены"
                )
            except:
                pass  # Игнорируем ошибку, если таблица уже удалена
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка удаления таблиц: {e}")
            return False
    
    def clear_table(self, table_name: str) -> bool:
        """
        Очистка конкретной таблицы
        
        Args:
            table_name (str): Название таблицы для очистки
            
        Returns:
            bool: True если очистка успешна, False иначе
        """
        try:
            with self.get_session() as session:
                # Получаем модель таблицы
                table_model = self._get_table_model(table_name)
                if not table_model:
                    logger.error(f"❌ Таблица '{table_name}' не найдена")
                    return False
                
                # Очищаем таблицу
                session.query(table_model).delete()
                logger.info(f"✅ Таблица '{table_name}' очищена")
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка очистки таблицы '{table_name}': {e}")
            return False
    
    def clear_all_tables(self) -> bool:
        """
        Очистка всех таблиц (сохранение структуры)
        
        Returns:
            bool: True если очистка успешна, False иначе
        """
        try:
            logger.info("🧹 Очистка всех таблиц...")
            
            # Список всех моделей в правильном порядке (с учетом внешних ключей)
            models = [BotMessage, BotLog, SearchHistory, Favorite, Blacklisted, 
                     UserSettings, Photo, VKUser]
            
            with self.get_session() as session:
                for model in models:
                    try:
                        session.query(model).delete()
                        logger.debug(f"Очищена таблица: {model.__tablename__}")
                    except Exception as e:
                        logger.error(f"Ошибка очистки таблицы {model.__tablename__}: {e}")
            
            logger.info("✅ Все таблицы очищены")
            
            # Логируем действие в БД
            self.add_bot_log(
                vk_user_id=0,  # Системный лог
                log_level="info",
                log_message="Все таблицы базы данных очищены"
            )
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка очистки всех таблиц: {e}")
            return False
    
    def get_table_info(self) -> Dict[str, Any]:
        """
        Получение информации о всех таблицах
        
        Returns:
            Dict[str, Any]: Словарь с информацией о таблицах
        """
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            info = {
                "total_tables": len(tables),
                "tables": {}
            }
            
            with self.get_session() as session:
                for table_name in tables:
                    try:
                        # Получаем модель таблицы
                        model = self._get_table_model(table_name)
                        if model:
                            try:
                                count = session.query(model).count()
                                info["tables"][table_name] = {
                                    "count": count,
                                    "model": model.__name__
                                }
                            except Exception as count_error:
                                logger.warning(f"Ошибка подсчета записей в таблице {table_name}: {count_error}")
                                info["tables"][table_name] = {
                                    "count": "error",
                                    "model": model.__name__
                                }
                        else:
                            info["tables"][table_name] = {
                                "count": "unknown",
                                "model": "unknown"
                            }
                    except Exception as e:
                        logger.error(f"Ошибка обработки таблицы {table_name}: {e}")
                        info["tables"][table_name] = {
                            "count": f"error: {e}",
                            "model": "unknown"
                        }
            
            return info
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации о таблицах: {e}")
            return {"error": str(e)}
    
    def _get_table_model(self, table_name: str):
        """Получение модели таблицы по названию"""
        table_models = {
            "vk_users": VKUser,
            "photos": Photo,
            "favorites": Favorite,
            "blacklisted": Blacklisted,
            "search_history": SearchHistory,
            "user_settings": UserSettings,
            "bot_logs": BotLog,
            "bot_messages": BotMessage
        }
        return table_models.get(table_name)
    
    # === CRUD ОПЕРАЦИИ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ===
    
    def add_user(self, vk_user_id: int, first_name: str, last_name: str, 
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
        try:
            with self.get_session() as session:
                # Проверяем, существует ли пользователь
                existing_user = session.query(VKUser).filter(VKUser.vk_user_id == vk_user_id).first()
                if existing_user:
                    logger.debug(f"Пользователь {vk_user_id} уже существует")
                    return True
                
                # Создаем нового пользователя
                user = VKUser(
                    vk_user_id=vk_user_id,
                    first_name=first_name,
                    last_name=last_name,
                    age=age,
                    sex=sex,
                    city=city,
                    country=country,
                    photo_url=photo_url
                )
                
                session.add(user)
                session.commit()
                logger.info(f"✅ Пользователь {vk_user_id} ({first_name} {last_name}) добавлен")
                
                # Логируем действие в БД
                self.add_bot_log(
                    vk_user_id=0,  # Системный лог
                    log_level="info",
                    log_message=f"Пользователь {vk_user_id} ({first_name} {last_name}) добавлен в БД"
                )
                return True
                
        except IntegrityError as e:
            logger.error(f"❌ Ошибка целостности при добавлении пользователя {vk_user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка добавления пользователя {vk_user_id}: {e}")
            return False
    
    def get_user(self, vk_user_id: int) -> Optional[VKUser]:
        """
        Получение пользователя по VK ID
        
        Args:
            vk_user_id (int): ID пользователя VK
            
        Returns:
            Optional[VKUser]: Пользователь или None
        """
        try:
            with self.get_session() as session:
                user = session.query(VKUser).filter(VKUser.vk_user_id == vk_user_id).first()
                return user
        except Exception as e:
            logger.error(f"❌ Ошибка получения пользователя {vk_user_id}: {e}")
            return None
    
    def update_user(self, vk_user_id: int, **kwargs) -> bool:
        """
        Обновление данных пользователя
        
        Args:
            vk_user_id (int): ID пользователя VK
            **kwargs: Поля для обновления
            
        Returns:
            bool: True если обновление успешно, False иначе
        """
        try:
            with self.get_session() as session:
                user = session.query(VKUser).filter(VKUser.vk_user_id == vk_user_id).first()
                if not user:
                    logger.error(f"❌ Пользователь {vk_user_id} не найден")
                    return False
                
                # Обновляем поля
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                
                logger.info(f"✅ Пользователь {vk_user_id} обновлен")
                
                # Логируем действие в БД
                self.add_bot_log(
                    vk_user_id=0,  # Системный лог
                    log_level="info",
                    log_message=f"Пользователь {vk_user_id} обновлен в БД"
                )
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления пользователя {vk_user_id}: {e}")
            return False
    
    def delete_user(self, vk_user_id: int) -> bool:
        """
        Удаление пользователя
        
        Args:
            vk_user_id (int): ID пользователя VK
            
        Returns:
            bool: True если удаление успешно, False иначе
        """
        try:
            with self.get_session() as session:
                user = session.query(VKUser).filter(VKUser.vk_user_id == vk_user_id).first()
                if not user:
                    logger.error(f"❌ Пользователь {vk_user_id} не найден")
                    return False
                
                session.delete(user)
                session.commit()
                logger.info(f"✅ Пользователь {vk_user_id} удален")
                
                # Логируем действие в БД
                self.add_bot_log(
                    vk_user_id=0,  # Системный лог
                    log_level="info",
                    log_message=f"Пользователь {vk_user_id} удален из БД"
                )
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка удаления пользователя {vk_user_id}: {e}")
            return False
    
    # === ОПЕРАЦИИ С ЛОГАМИ ===
    
    def add_bot_log(self, vk_user_id: int, log_level: str, log_message: str) -> bool:
        """
        Добавление лога в базу данных
        
        Args:
            vk_user_id (int): ID пользователя VK (0 для системных логов)
            log_level (str): Уровень логирования
            log_message (str): Текст лога
            
        Returns:
            bool: True если добавление успешно, False иначе
        """
        try:
            with self.get_session() as session:
                log_entry = BotLog(
                    vk_user_id=vk_user_id,
                    log_level=log_level,
                    log_message=log_message
                )
                session.add(log_entry)
                logger.debug(f"Лог добавлен: {log_level} - {log_message}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка добавления лога: {e}")
            return False
    
    def get_bot_logs(self, vk_user_id: int = 0, log_level: str = None, limit: int = 100) -> List[BotLog]:
        """
        Получение логов бота
        
        Args:
            vk_user_id (int): ID пользователя VK (0 для всех)
            log_level (str): Уровень логирования
            limit (int): Максимальное количество записей
            
        Returns:
            List[BotLog]: Список логов
        """
        try:
            with self.get_session() as session:
                query = session.query(BotLog)
                
                if vk_user_id != 0:
                    query = query.filter(BotLog.vk_user_id == vk_user_id)
                
                if log_level:
                    query = query.filter(BotLog.log_level == log_level)
                
                logs = query.order_by(BotLog.created_at.desc()).limit(limit).all()
                # Преобразуем объекты в словари для избежания проблем с сессией
                result = []
                for log in logs:
                    result.append({
                        'id': log.id,
                        'vk_user_id': log.vk_user_id,
                        'log_level': log.log_level,
                        'log_message': log.log_message,
                        'created_at': log.created_at
                    })
                return result
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения логов: {e}")
            return []
    
    # === ОПЕРАЦИИ С СООБЩЕНИЯМИ ===
    
    def add_bot_message(self, vk_user_id: int, message_type: str, message_text: str) -> bool:
        """
        Добавление сообщения бота
        
        Args:
            vk_user_id (int): ID пользователя VK
            message_type (str): Тип сообщения (command, response, error)
            message_text (str): Текст сообщения
            
        Returns:
            bool: True если добавление успешно, False иначе
        """
        try:
            with self.get_session() as session:
                message = BotMessage(
                    vk_user_id=vk_user_id,
                    message_type=message_type,
                    message_text=message_text
                )
                session.add(message)
                logger.debug(f"Сообщение добавлено: {message_type} - {message_text[:50]}...")
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка добавления сообщения: {e}")
            return False
    
    def get_user_messages(self, vk_user_id: int, limit: int = 50) -> List[BotMessage]:
        """
        Получение сообщений пользователя
        
        Args:
            vk_user_id (int): ID пользователя VK
            limit (int): Максимальное количество сообщений
            
        Returns:
            List[BotMessage]: Список сообщений
        """
        try:
            with self.get_session() as session:
                messages = (session.query(BotMessage)
                          .filter(BotMessage.vk_user_id == vk_user_id)
                          .order_by(BotMessage.sent_at.desc())
                          .limit(limit)
                          .all())
                # Преобразуем объекты в словари для избежания проблем с сессией
                result = []
                for msg in messages:
                    result.append({
                        'id': msg.id,
                        'vk_user_id': msg.vk_user_id,
                        'message_type': msg.message_type,
                        'message_text': msg.message_text,
                        'sent_at': msg.sent_at
                    })
                return result
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения сообщений пользователя {vk_user_id}: {e}")
            return []
    
    # === ОПЕРАЦИИ С ИЗБРАННЫМ ===
    
    def add_favorite(self, user_vk_id: int, favorite_vk_id: int) -> bool:
        """
        Добавление в избранное
        
        Args:
            user_vk_id (int): ID пользователя, который добавляет
            favorite_vk_id (int): ID пользователя, которого добавляют
            
        Returns:
            bool: True если добавление успешно, False иначе
        """
        try:
            with self.get_session() as session:
                # Проверяем, не добавлен ли уже
                existing = (session.query(Favorite)
                          .filter(Favorite.user_vk_id == user_vk_id)
                          .filter(Favorite.favorite_vk_id == favorite_vk_id)
                          .first())
                
                if existing:
                    logger.debug(f"Пользователь {favorite_vk_id} уже в избранном у {user_vk_id}")
                    return True
                
                favorite = Favorite(
                    user_vk_id=user_vk_id,
                    favorite_vk_id=favorite_vk_id
                )
                session.add(favorite)
                session.commit()
                logger.info(f"✅ Пользователь {favorite_vk_id} добавлен в избранное к {user_vk_id}")
                
                # Логируем действие в БД
                self.add_bot_log(
                    vk_user_id=0,  # Системный лог
                    log_level="info",
                    log_message=f"Пользователь {favorite_vk_id} добавлен в избранное к {user_vk_id}"
                )
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка добавления в избранное: {e}")
            return False
    
    def get_favorites(self, user_vk_id: int) -> List[Favorite]:
        """
        Получение списка избранных пользователя
        
        Args:
            user_vk_id (int): ID пользователя VK
            
        Returns:
            List[Favorite]: Список избранных
        """
        try:
            with self.get_session() as session:
                favorites = (session.query(Favorite)
                           .filter(Favorite.user_vk_id == user_vk_id)
                           .order_by(Favorite.created_at.desc())
                           .limit(10)
                           .all())
                # Преобразуем объекты в словари для избежания проблем с сессией
                result = []
                for fav in favorites:
                    result.append({
                        'id': fav.id,
                        'user_vk_id': fav.user_vk_id,
                        'favorite_vk_id': fav.favorite_vk_id,
                        'created_at': fav.created_at
                    })
                return result
                
        except Exception as e:
            logger.error(f"❌ Ошибка получения избранных для {user_vk_id}: {e}")
            return []
    
    def remove_favorite(self, user_vk_id: int, favorite_vk_id: int) -> bool:
        """
        Удаление из избранного
        
        Args:
            user_vk_id (int): ID пользователя
            favorite_vk_id (int): ID пользователя для удаления
            
        Returns:
            bool: True если удаление успешно, False иначе
        """
        try:
            with self.get_session() as session:
                favorite = (session.query(Favorite)
                          .filter(Favorite.user_vk_id == user_vk_id)
                          .filter(Favorite.favorite_vk_id == favorite_vk_id)
                          .first())
                
                if not favorite:
                    logger.debug(f"Пользователь {favorite_vk_id} не найден в избранном у {user_vk_id}")
                    return True
                
                session.delete(favorite)
                session.commit()
                logger.info(f"✅ Пользователь {favorite_vk_id} удален из избранного у {user_vk_id}")
                
                # Логируем действие в БД
                self.add_bot_log(
                    vk_user_id=0,  # Системный лог
                    log_level="info",
                    log_message=f"Пользователь {favorite_vk_id} удален из избранного у {user_vk_id}"
                )
                return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка удаления из избранного: {e}")
            return False

    # === УПРАВЛЕНИЕ ЧЕРНЫМ СПИСКОМ ===

    def add_to_blacklist(self, user_id: int, blacklisted_id: int) -> bool:
        """
        Добавление пользователя в черный список
        
        Args:
            user_id: ID пользователя, который добавляет в черный список
            blacklisted_id: ID пользователя, которого добавляют в черный список
            
        Returns:
            bool: True если добавление успешно, False иначе
        """
        try:
            with self.get_session() as session:
                # Проверяем, есть ли уже в черном списке
                existing = session.query(Blacklisted).filter(
                    Blacklisted.user_vk_id == user_id,
                    Blacklisted.blocked_vk_id == blacklisted_id
                ).first()
                
                if existing:
                    self.logger.warning(f"Пользователь {blacklisted_id} уже в черном списке пользователя {user_id}")
                    return True
                
                # Добавляем в черный список
                blacklisted = Blacklisted(
                    user_vk_id=user_id,
                    blocked_vk_id=blacklisted_id,
                    created_at=datetime.now()
                )
                session.add(blacklisted)
                session.commit()
                
                self.logger.info(f"Пользователь {blacklisted_id} добавлен в черный список пользователя {user_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Ошибка добавления в черный список: {e}")
            return False

    def get_blacklisted(self, user_id: int) -> List[int]:
        """
        Получение списка ID пользователей в черном списке
        
        Args:
            user_id: ID пользователя
            
        Returns:
            List[int]: Список ID пользователей в черном списке
        """
        try:
            with self.get_session() as session:
                blacklisted = session.query(Blacklisted).filter(
                    Blacklisted.user_vk_id == user_id
                ).all()
                
                return [b.blocked_vk_id for b in blacklisted]
                
        except Exception as e:
            self.logger.error(f"Ошибка получения черного списка: {e}")
            return []

    def remove_from_blacklist(self, user_id: int, blacklisted_id: int) -> bool:
        """
        Удаление пользователя из черного списка
        
        Args:
            user_id: ID пользователя, который удаляет из черного списка
            blacklisted_id: ID пользователя, которого удаляют из черного списка
            
        Returns:
            bool: True если удаление успешно, False иначе
        """
        try:
            with self.get_session() as session:
                blacklisted = session.query(Blacklisted).filter(
                    Blacklisted.user_vk_id == user_id,
                    Blacklisted.blocked_vk_id == blacklisted_id
                ).first()
                
                if not blacklisted:
                    self.logger.warning(f"Пользователь {blacklisted_id} не найден в черном списке пользователя {user_id}")
                    return False
                
                session.delete(blacklisted)
                session.commit()
                
                self.logger.info(f"Пользователь {blacklisted_id} удален из черного списка пользователя {user_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Ошибка удаления из черного списка: {e}")
            return False

    def get_user_statistics(self, user_id: int) -> dict:
        """
        Получение статистики пользователя из базы данных
        
        Args:
            user_id: ID пользователя VK
            
        Returns:
            dict: Словарь со статистикой пользователя
        """
        try:
            stats = {}
            
            with self.get_session() as session:
                # Количество просмотренных анкет (уникальные пользователи в vk_users, найденные этим пользователем)
                try:
                    # Считаем количество уникальных пользователей, которых нашел этот пользователь
                    # через фотографии, которые он нашел
                    viewed_count = session.query(Photo).filter(
                        Photo.found_by_user_id == user_id
                    ).with_entities(Photo.vk_user_id).distinct().count()
                    stats['viewed_profiles'] = viewed_count
                except Exception as e:
                    logger.error(f"❌ Ошибка получения количества просмотренных анкет: {e}")
                    stats['viewed_profiles'] = 0
                
                # Получаем количество избранных и заблокированных
                try:
                    favorites_count = session.query(Favorite).filter(
                        Favorite.user_vk_id == user_id
                    ).count()
                    stats['favorites_count'] = favorites_count
                except Exception as e:
                    logger.error(f"❌ Ошибка получения количества избранных: {e}")
                    stats['favorites_count'] = 0
                
                try:
                    blacklisted_count = session.query(Blacklisted).filter(
                        Blacklisted.user_vk_id == user_id
                    ).count()
                    stats['blacklisted_count'] = blacklisted_count
                except Exception as e:
                    logger.error(f"❌ Ошибка получения количества заблокированных: {e}")
                    stats['blacklisted_count'] = 0
                
                # Количество просмотренных фотографий
                try:
                    viewed_photos = session.query(Photo).filter(
                        Photo.found_by_user_id == user_id
                    ).count()
                    stats['viewed_photos'] = viewed_photos
                except Exception as e:
                    logger.error(f"❌ Ошибка получения количества просмотренных фото: {e}")
                    stats['viewed_photos'] = 0
                
                # Количество поисковых сессий
                try:
                    search_sessions = session.query(SearchHistory).filter(
                        SearchHistory.user_vk_id == user_id
                    ).count()
                    stats['search_sessions'] = search_sessions
                except Exception as e:
                    logger.error(f"❌ Ошибка получения количества поисков: {e}")
                    stats['search_sessions'] = 0
            
            logger.info(f"✅ Статистика пользователя {user_id} получена: {len(stats)} показателей")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики пользователя: {e}")
            return {}


def main():
    """Основная функция для тестирования интерфейса базы данных"""
    print("🔧 Тестирование интерфейса базы данных VKinder Bot")
    print("=" * 60)
    
    # Создаем экземпляр интерфейса
    db_interface = DatabaseInterface()
    
    # Тестируем подключение
    print("\n1. Тестирование подключения...")
    if db_interface.test_connection():
        print("✅ Подключение работает")
    else:
        print("❌ Ошибка подключения")
        return
    
    # Получаем информацию о таблицах
    print("\n2. Информация о таблицах...")
    table_info = db_interface.get_table_info()
    print(f"📊 Всего таблиц: {table_info.get('total_tables', 0)}")
    
    for table_name, info in table_info.get('tables', {}).items():
        print(f"  - {table_name}: {info['count']} записей")
    
    # Тестируем добавление пользователя
    print("\n3. Тестирование добавления пользователя...")
    test_user_id = 123456789
    if db_interface.add_user(
        vk_user_id=test_user_id,
        first_name="Тест",
        last_name="Пользователь",
        age=25,
        sex=2,
        city="Москва"
    ):
        print("✅ Пользователь добавлен")
    else:
        print("❌ Ошибка добавления пользователя")
    
    # Тестируем добавление лога
    print("\n4. Тестирование добавления лога...")
    if db_interface.add_bot_log(
        vk_user_id=test_user_id,
        log_level="info",
        log_message="Тестовое сообщение от интерфейса БД"
    ):
        print("✅ Лог добавлен")
    else:
        print("❌ Ошибка добавления лога")
    
    # Тестируем добавление сообщения
    print("\n5. Тестирование добавления сообщения...")
    if db_interface.add_bot_message(
        vk_user_id=test_user_id,
        message_type="command",
        message_text="/start"
    ):
        print("✅ Сообщение добавлено")
    else:
        print("❌ Ошибка добавления сообщения")
    
    # Получаем обновленную информацию
    print("\n6. Обновленная информация о таблицах...")
    table_info = db_interface.get_table_info()
    for table_name, info in table_info.get('tables', {}).items():
        print(f"  - {table_name}: {info['count']} записей")
    
    print("\n✅ Тестирование завершено!")


if __name__ == "__main__":
    main()
