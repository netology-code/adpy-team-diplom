#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для настройки переменных окружения
Создает файл .env с необходимыми параметрами
"""

import os

def create_env_file():
    """Создание файла .env с настройками бота"""
    
    env_content = """# VK Bot Configuration
# ВАЖНО: Замените значения ниже на ваши реальные данные!
VK_GROUP_TOKEN=your_group_token_here
VK_GROUP_ID=your_group_id_here
VK_APP_ID=your_app_id_here
VK_APP_SECRET=your_app_secret_here
VK_SERVICE_KEY=your_service_key_here

# Bot Settings
BOT_NAME=VKinder Bot
GROUP_LINK=https://vk.com/your_group_link

# Logging Settings
LOG_LEVEL=INFO
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Файл .env создан успешно")
        print("⚠️  ВАЖНО: Замените значения в .env на ваши реальные данные!")
        print("📋 Пример конфигурации: env.example")
        print("🔒 Файл .env автоматически исключен из Git для безопасности")
        
    except Exception as e:
        print(f"❌ Ошибка при создании файла .env: {e}")

def main():
    """Главная функция"""
    create_env_file()

if __name__ == "__main__":
    main()
