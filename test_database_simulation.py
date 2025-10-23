#!/usr/bin/env python3
"""
Симуляция работы системы для тестирования базы данных
Эмулирует работу бота с пользователями, логированием и сообщениями
"""

import sys
import os
import time
import random
from datetime import datetime
from typing import List, Dict, Any

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_api import *


class DatabaseSimulator:
    """Симулятор работы системы для тестирования базы данных"""
    
    def __init__(self):
        """Инициализация симулятора"""
        self.users = []
        self.simulation_running = False
        
    def start_simulation(self):
        """Запуск симуляции"""
        print("🚀 ЗАПУСК СИМУЛЯЦИИ РАБОТЫ СИСТЕМЫ")
        print("=" * 50)
        
        # Проверяем подключение к БД
        if not test_database():
            print("❌ Ошибка подключения к базе данных")
            return False
        
        print("✅ Подключение к базе данных работает")
        
        # Создаем тестовых пользователей
        self.create_test_users()
        
        # Запускаем симуляцию
        self.simulation_running = True
        self.run_simulation()
        
        return True
    
    def create_test_users(self):
        """Создание тестовых пользователей"""
        print("\n👥 Создание тестовых пользователей...")
        
        test_users = [
            {"vk_user_id": 1001, "first_name": "Анна", "last_name": "Иванова", "age": 25, "sex": 1, "city": "Москва"},
            {"vk_user_id": 1002, "first_name": "Петр", "last_name": "Петров", "age": 30, "sex": 2, "city": "СПб"},
            {"vk_user_id": 1003, "first_name": "Мария", "last_name": "Сидорова", "age": 28, "sex": 1, "city": "Казань"},
            {"vk_user_id": 1004, "first_name": "Алексей", "last_name": "Козлов", "age": 32, "sex": 2, "city": "Новосибирск"},
            {"vk_user_id": 1005, "first_name": "Елена", "last_name": "Морозова", "age": 27, "sex": 1, "city": "Екатеринбург"}
        ]
        
        for user_data in test_users:
            if add_user(**user_data):
                self.users.append(user_data['vk_user_id'])
                print(f"  ✅ {user_data['first_name']} {user_data['last_name']} добавлен")
            else:
                print(f"  ❌ Ошибка добавления {user_data['first_name']}")
        
        print(f"📊 Создано пользователей: {len(self.users)}")
    
    def run_simulation(self):
        """Запуск основной симуляции"""
        print("\n🎭 Начало симуляции работы системы...")
        print("💡 Симуляция будет работать 30 секунд")
        print("⏹️  Нажмите Ctrl+C для остановки")
        
        start_time = time.time()
        cycle = 0
        
        try:
            while self.simulation_running and (time.time() - start_time) < 30:
                cycle += 1
                print(f"\n🔄 Цикл {cycle}")
                
                # Симулируем различные события
                self.simulate_user_activity()
                self.simulate_system_events()
                self.simulate_messages()
                self.simulate_favorites()
                
                # Пауза между циклами
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n⏹️  Симуляция остановлена пользователем")
        
        print(f"\n✅ Симуляция завершена за {cycle} циклов")
        self.show_simulation_results()
    
    def simulate_user_activity(self):
        """Симуляция активности пользователей"""
        if not self.users:
            return
        
        # Выбираем случайного пользователя
        user_id = random.choice(self.users)
        
        # Симулируем различные действия
        actions = [
            "зашел в систему",
            "начал поиск пользователей",
            "просматривает профили",
            "обновил настройки",
            "вышел из системы"
        ]
        
        action = random.choice(actions)
        log_info(f"Пользователь {user_id} {action}", user_id)
        
        # Симулируем ошибки (10% вероятность)
        if random.random() < 0.1:
            error_messages = [
                "Ошибка загрузки фотографий",
                "Таймаут подключения к API",
                "Ошибка валидации данных",
                "Недостаточно прав доступа"
            ]
            error = random.choice(error_messages)
            log_error(f"{error} для пользователя {user_id}", user_id)
    
    def simulate_system_events(self):
        """Симуляция системных событий"""
        events = [
            "Система запущена",
            "Проверка подключения к БД",
            "Очистка временных файлов",
            "Обновление кэша",
            "Резервное копирование данных"
        ]
        
        event = random.choice(events)
        log_info(event)
        
        # Симулируем системные ошибки (5% вероятность)
        if random.random() < 0.05:
            system_errors = [
                "Высокое использование памяти",
                "Медленный ответ БД",
                "Превышен лимит подключений",
                "Ошибка записи в лог"
            ]
            error = random.choice(system_errors)
            log_warning(error)
    
    def simulate_messages(self):
        """Симуляция сообщений между пользователями и системой"""
        if not self.users:
            return
        
        user_id = random.choice(self.users)
        
        # Команды пользователей
        commands = [
            "/start",
            "/help", 
            "/search",
            "/favorites",
            "/settings",
            "/profile"
        ]
        
        command = random.choice(commands)
        add_message(user_id, "command", command)
        
        # Ответы системы
        responses = {
            "/start": "Добро пожаловать в систему!",
            "/help": "Доступные команды: /start, /search, /favorites",
            "/search": "Начинаю поиск подходящих пользователей...",
            "/favorites": "Ваши избранные пользователи:",
            "/settings": "Настройки системы:",
            "/profile": "Ваш профиль:"
        }
        
        response = responses.get(command, "Команда обработана")
        add_message(user_id, "response", response)
        
        # Симулируем ошибки (15% вероятность)
        if random.random() < 0.15:
            error_messages = [
                "Ошибка: команда не распознана",
                "Ошибка: недостаточно прав",
                "Ошибка: временная недоступность",
                "Ошибка: неверный формат данных"
            ]
            error = random.choice(error_messages)
            add_message(user_id, "error", error)
    
    def simulate_favorites(self):
        """Симуляция работы с избранным"""
        if len(self.users) < 2:
            return
        
        # Выбираем двух разных пользователей
        user_id = random.choice(self.users)
        other_users = [u for u in self.users if u != user_id]
        favorite_id = random.choice(other_users)
        
        # Симулируем добавление в избранное (30% вероятность)
        if random.random() < 0.3:
            if add_favorite(user_id, favorite_id):
                log_info(f"Пользователь {user_id} добавил {favorite_id} в избранное", user_id)
        
        # Симулируем удаление из избранного (10% вероятность)
        if random.random() < 0.1:
            favorites = get_favorites(user_id)
            if favorites:
                fav_to_remove = random.choice(favorites)['favorite_vk_id']
                if remove_favorite(user_id, fav_to_remove):
                    log_info(f"Пользователь {user_id} удалил {fav_to_remove} из избранного", user_id)
    
    def show_simulation_results(self):
        """Показать результаты симуляции"""
        print("\n📊 РЕЗУЛЬТАТЫ СИМУЛЯЦИИ")
        print("=" * 50)
        
        # Информация о БД
        info = get_database_info()
        print(f"📋 Всего таблиц: {info.get('total_tables', 0)}")
        
        for table_name, table_info in info.get('tables', {}).items():
            print(f"  📄 {table_name}: {table_info['count']} записей")
        
        # Статистика логов
        print(f"\n📝 Логи:")
        total_logs = sum(1 for table_info in info.get('tables', {}).values() 
                        if 'bot_logs' in str(table_info))
        
        # Получаем последние логи
        recent_logs = get_logs(limit=5)
        print(f"  📊 Всего логов: {len(recent_logs)}")
        print("  📋 Последние логи:")
        for log in recent_logs:
            user_info = f"Пользователь {log['vk_user_id']}" if log['vk_user_id'] != 0 else "Система"
            print(f"    [{log['log_level'].upper()}] {user_info}: {log['log_message']}")
        
        # Статистика сообщений
        print(f"\n💬 Сообщения:")
        for user_id in self.users[:3]:  # Показываем для первых 3 пользователей
            messages = get_user_messages(user_id, limit=3)
            print(f"  👤 Пользователь {user_id}: {len(messages)} сообщений")
        
        # Статистика избранного
        print(f"\n❤️ Избранное:")
        for user_id in self.users[:3]:
            favorites = get_favorites(user_id)
            print(f"  👤 Пользователь {user_id}: {len(favorites)} избранных")
        
        print(f"\n✅ Симуляция завершена успешно!")


def main():
    """Основная функция"""
    print("🧪 ТЕСТИРОВАНИЕ БАЗЫ ДАННЫХ С СИМУЛЯЦИЕЙ")
    print("=" * 60)
    
    # Создаем симулятор
    simulator = DatabaseSimulator()
    
    # Запускаем симуляцию
    success = simulator.start_simulation()
    
    if success:
        print("\n🎉 Тестирование завершено успешно!")
        print("📖 Дополнительная документация:")
        print("  - DATABASE_INTERFACE_GUIDE.md")
        print("  - DATABASE_COMMANDS_REFERENCE.md")
        print("  - database_examples.py")
    else:
        print("\n❌ Тестирование завершено с ошибками")
        print("🔧 Проверьте настройки базы данных")


if __name__ == "__main__":
    main()
