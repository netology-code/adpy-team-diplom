#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Настройки бота - управление конфигурацией
"""

import os
from dotenv import load_dotenv

class BotSettings:
    """Класс для управления настройками бота"""
    
    def __init__(self):
        """Инициализация настроек"""
        # Загружаем переменные окружения
        load_dotenv()
        
        # VK API настройки
        self.VK_GROUP_TOKEN = os.getenv('VK_GROUP_TOKEN')
        self.VK_GROUP_ID = int(os.getenv('VK_GROUP_ID', 0))
        self.VK_APP_ID = os.getenv('VK_APP_ID')
        self.VK_APP_SECRET = os.getenv('VK_APP_SECRET')
        self.VK_SERVICE_KEY = os.getenv('VK_SERVICE_KEY')
        self.VK_USER_TOKEN = os.getenv('VK_USER_TOKEN')
        
        # Настройки бота
        self.BOT_NAME = os.getenv('BOT_NAME', 'VKinder Bot')
        self.GROUP_LINK = os.getenv('GROUP_LINK', 'https://vk.com/your_group')
        
        # Настройки логирования
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        
        # Настройки бота
        self.ENABLE_STOP_COMMAND = os.getenv('ENABLE_STOP_COMMAND', 'true').lower() == 'true'
        
        # Параметры для тестирования интерактивного ввода данных
        self.TEST_HIDDEN_AGE = os.getenv('TEST_HIDDEN_AGE', 'false').lower() == 'true'
        self.TEST_HIDDEN_SEX = os.getenv('TEST_HIDDEN_SEX', 'false').lower() == 'true'
        self.TEST_HIDDEN_CITY = os.getenv('TEST_HIDDEN_CITY', 'false').lower() == 'true'
        
        # Проверяем обязательные настройки
        self._validate_settings()
    
    def _validate_settings(self):
        """Проверка обязательных настроек"""
        required_settings = {
            'VK_GROUP_TOKEN': self.VK_GROUP_TOKEN,
            'VK_GROUP_ID': self.VK_GROUP_ID,
            'VK_APP_ID': self.VK_APP_ID,
            'VK_APP_SECRET': self.VK_APP_SECRET,
            'VK_SERVICE_KEY': self.VK_SERVICE_KEY
        }
        
        missing_settings = []
        for name, value in required_settings.items():
            if not value:
                missing_settings.append(name)
        
        if missing_settings:
            raise ValueError(f"Отсутствуют обязательные настройки: {', '.join(missing_settings)}")
    
    def get_settings_info(self) -> dict:
        """Получение информации о настройках"""
        return {
            'bot_name': self.BOT_NAME,
            'group_link': self.GROUP_LINK,
            'log_level': self.LOG_LEVEL,
            'vk_group_id': self.VK_GROUP_ID,
            'vk_app_id': self.VK_APP_ID,
            'has_group_token': bool(self.VK_GROUP_TOKEN),
            'has_app_secret': bool(self.VK_APP_SECRET),
            'has_service_key': bool(self.VK_SERVICE_KEY),
            'has_user_token': bool(self.VK_USER_TOKEN)
        }
