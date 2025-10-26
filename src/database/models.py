"""
Модели базы данных для системы управления PostgreSQL
Определяет структуру всех таблиц для работы с пользователями, поиском и избранным
"""

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List

# Базовый класс для всех моделей
Base = declarative_base()


class VKUser(Base):
    """
    Модель пользователя VK
    
    Хранит основную информацию о пользователях ВКонтакте:
    - ID пользователя, имя, фамилия
    - Возраст, пол, город
    - URL фотографии профиля
    - Статус активности
    """
    __tablename__ = "vk_users"
    
    # Основные поля
    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_user_id = Column(BigInteger, unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=True)
    sex = Column(Integer, nullable=True)  # 1 - женский, 2 - мужской
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    bdate = Column(String(20), nullable=True)
    photo_url = Column(String(500), nullable=True)
    profile_url = Column(String(200), nullable=True)
    is_closed = Column(Boolean, default=False, nullable=True)
    can_access_closed = Column(Boolean, default=False, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи с другими таблицами
    photos = relationship("Photo", foreign_keys="Photo.vk_user_id", back_populates="user", cascade="all, delete-orphan")
    favorites = relationship("Favorite", foreign_keys="Favorite.user_vk_id", back_populates="user")
    blacklisted_by = relationship("Blacklisted", foreign_keys="Blacklisted.user_vk_id", back_populates="user")
    search_history = relationship("SearchHistory", back_populates="user")
    user_settings = relationship("UserSettings", back_populates="user", uselist=False)
    bot_messages = relationship("BotMessage", back_populates="user")
    
    @property
    def full_name(self) -> str:
        """Полное имя пользователя"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self) -> str:
        """Строковое представление пользователя"""
        return f"<VKUser(id={self.vk_user_id}, name='{self.full_name}')>"


class Photo(Base):
    """
    Модель фотографии пользователя
    
    Хранит информацию о фотографиях пользователей:
    - Ссылка на фотографию
    - Тип фотографии (profile, album, etc.)
    - Количество лайков и дизлайков
    - Кто нашел эту фотографию в поиске
    """
    __tablename__ = "photos"
    
    # Основные поля
    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_user_id = Column(Integer, ForeignKey("vk_users.vk_user_id"), nullable=False)
    photo_url = Column(Text, nullable=False)
    photo_type = Column(String(50), nullable=True)  # profile, album, etc.
    likes_count = Column(Integer, default=0, nullable=False)
    
    # Поле для отслеживания того, кто нашел эту фотографию
    found_by_user_id = Column(Integer, ForeignKey("vk_users.vk_user_id"), nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    user = relationship("VKUser", foreign_keys=[vk_user_id], back_populates="photos")
    found_by_user = relationship("VKUser", foreign_keys=[found_by_user_id])
    
    def __repr__(self) -> str:
        """Строковое представление фотографии"""
        return f"<Photo(id={self.id}, user_id={self.vk_user_id}, type='{self.photo_type}')>"


class Favorite(Base):
    """
    Модель избранных пользователей
    
    Связывает пользователей с их избранными:
    - Кто добавил в избранное
    - Кого добавили в избранное
    """
    __tablename__ = "favorites"
    
    # Основные поля
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_vk_id = Column(Integer, ForeignKey("vk_users.vk_user_id"), nullable=False)
    favorite_vk_id = Column(Integer, ForeignKey("vk_users.vk_user_id"), nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    user = relationship("VKUser", foreign_keys=[user_vk_id], back_populates="favorites")
    favorite = relationship("VKUser", foreign_keys=[favorite_vk_id])
    
    def __repr__(self) -> str:
        """Строковое представление избранного"""
        return f"<Favorite(user_id={self.user_vk_id}, favorite_id={self.favorite_vk_id})>"


class Blacklisted(Base):
    """
    Модель черного списка
    
    Связывает пользователей с заблокированными:
    - Кто заблокировал
    - Кого заблокировали
    """
    __tablename__ = "blacklisted"
    
    # Основные поля
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_vk_id = Column(Integer, ForeignKey("vk_users.vk_user_id"), nullable=False)
    blocked_vk_id = Column(Integer, ForeignKey("vk_users.vk_user_id"), nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    user = relationship("VKUser", foreign_keys=[user_vk_id], back_populates="blacklisted_by")
    blocked = relationship("VKUser", foreign_keys=[blocked_vk_id])
    
    def __repr__(self) -> str:
        """Строковое представление черного списка"""
        return f"<Blacklisted(user_id={self.user_vk_id}, blocked_id={self.blocked_vk_id})>"


class SearchHistory(Base):
    """
    Модель истории поиска
    
    Хранит информацию о поисковых запросах:
    - Параметры поиска (возраст, пол, город, статусы)
    - Количество найденных результатов
    - Время поиска
    """
    __tablename__ = "search_history"
    
    # Основные поля
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_vk_id = Column(Integer, ForeignKey("vk_users.vk_user_id"), nullable=False)
    results_count = Column(Integer, default=0, nullable=False)
    
    # Отдельные поля для параметров поиска
    target_sex = Column(String(20), nullable=True)  # Мужской/Женский
    age_from = Column(Integer, nullable=True)  # Минимальный возраст
    age_to = Column(Integer, nullable=True)  # Максимальный возраст
    city = Column(String(100), nullable=True)  # Город поиска
    city_id = Column(Integer, nullable=True)  # ID города
    
    # Поля для статусов
    relationship_status = Column(String(50), nullable=True)  # single, married, divorced, etc.
    online = Column(Boolean, nullable=True)  # Только онлайн
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    user = relationship("VKUser", back_populates="search_history")
    
    def __repr__(self) -> str:
        """Строковое представление истории поиска"""
        return f"<SearchHistory(id={self.id}, user_id={self.user_vk_id}, results={self.results_count})>"


class UserSettings(Base):
    """
    Модель настроек пользователя
    
    Хранит персональные настройки поиска:
    - Возрастной диапазон
    - Предпочтения по полу
    - Предпочтения по городу
    - Статусы отношений
    """
    __tablename__ = "user_settings"
    
    # Основные поля
    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_user_id = Column(Integer, ForeignKey("vk_users.vk_user_id"), nullable=False, unique=True)
    min_age = Column(Integer, default=18, nullable=False)
    max_age = Column(Integer, default=35, nullable=False)
    sex_preference = Column(Integer, nullable=True)  # 1 - женский, 2 - мужской, 0 - любой
    city_preference = Column(String(100), nullable=True)
    
    # Новые поля для статусов
    relationship_status = Column(String(50), nullable=True)  # single, married, divorced, etc.
    online = Column(Boolean, default=False, nullable=True)  # Только онлайн
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    user = relationship("VKUser", back_populates="user_settings")
    
    def __repr__(self) -> str:
        """Строковое представление настроек пользователя"""
        return f"<UserSettings(user_id={self.vk_user_id}, age={self.min_age}-{self.max_age})>"


class BotLog(Base):
    """
    Модель логов бота
    
    Хранит системные логи работы бота:
    - Уровень логирования (info, debug, error, warning)
    - Текст лога
    - Время создания
    - ID пользователя (0 для системных логов)
    """
    __tablename__ = "bot_logs"
    
    # Основные поля
    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_user_id = Column(Integer, nullable=False, default=0)  # 0 для системных логов
    log_level = Column(String(20), nullable=False)  # info, debug, error, warning, success
    log_message = Column(Text, nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self) -> str:
        """Строковое представление лога бота"""
        return f"<BotLog(id={self.id}, level='{self.log_level}', user_id={self.vk_user_id})>"


class BotMessage(Base):
    """
    Модель сообщений бота
    
    Хранит историю сообщений между ботом и пользователями:
    - Тип сообщения (command, response, error)
    - Текст сообщения
    - Время отправки
    """
    __tablename__ = "bot_messages"
    
    # Основные поля
    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_user_id = Column(Integer, ForeignKey("vk_users.vk_user_id"), nullable=False)
    message_type = Column(String(50), nullable=False)  # command, response, error
    message_text = Column(Text, nullable=False)
    
    # Временные метки
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    user = relationship("VKUser", back_populates="bot_messages")
    
    def __repr__(self) -> str:
        """Строковое представление сообщения бота"""
        return f"<BotMessage(id={self.id}, user_id={self.vk_user_id}, type='{self.message_type}')>"
