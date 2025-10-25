#!/usr/bin/env python3
"""
CLI интерфейс для управления базой данных VKinder Bot
Предоставляет команды для создания, удаления, очистки и управления БД
"""

import sys
import argparse
from typing import List, Optional

# Исправляем импорты для работы как отдельного скрипта
try:
    from .database_interface import DatabaseInterface
    from .postgres_manager import PostgreSQLManager
except ImportError:
    # Если относительные импорты не работают, используем абсолютные
    from database_interface import DatabaseInterface
    from postgres_manager import PostgreSQLManager

from loguru import logger


class DatabaseCLI:
    """CLI интерфейс для управления базой данных"""
    
    def __init__(self):
        """Инициализация CLI"""
        self.db_interface = DatabaseInterface()
        self.postgres_manager = PostgreSQLManager()
    
    def create_database(self) -> bool:
        """Создание всех таблиц базы данных"""
        print("🔨 Создание таблиц базы данных...")
        return self.db_interface.create_database()
    
    def drop_database(self) -> bool:
        """Удаление всех таблиц базы данных"""
        print("🗑️ Удаление всех таблиц...")
        confirm = input("⚠️  Вы уверены? Это удалит ВСЕ данные! (yes/no): ")
        if confirm.lower() in ['yes', 'y', 'да', 'д']:
            return self.db_interface.drop_database()
        else:
            print("❌ Операция отменена")
            return False
    
    def clear_table(self, table_name: str) -> bool:
        """Очистка конкретной таблицы"""
        print(f"🧹 Очистка таблицы '{table_name}'...")
        return self.db_interface.clear_table(table_name)
    
    def clear_all_tables(self) -> bool:
        """Очистка всех таблиц"""
        print("🧹 Очистка всех таблиц...")
        confirm = input("⚠️  Вы уверены? Это удалит ВСЕ данные! (yes/no): ")
        if confirm.lower() in ['yes', 'y', 'да', 'д']:
            return self.db_interface.clear_all_tables()
        else:
            print("❌ Операция отменена")
            return False
    
    def show_info(self) -> None:
        """Показать информацию о базе данных"""
        print("📊 Информация о базе данных:")
        print("=" * 50)
        
        # Тестируем подключение
        if not self.db_interface.test_connection():
            print("❌ Ошибка подключения к базе данных")
            return
        
        # Получаем информацию о таблицах
        table_info = self.db_interface.get_table_info()
        
        if "error" in table_info:
            print(f"❌ Ошибка получения информации: {table_info['error']}")
            return
        
        print(f"📋 Всего таблиц: {table_info.get('total_tables', 0)}")
        print()
        
        for table_name, info in table_info.get('tables', {}).items():
            count = info.get('count', 'unknown')
            model = info.get('model', 'unknown')
            print(f"  📄 {table_name}")
            print(f"     - Записей: {count}")
            print(f"     - Модель: {model}")
            print()
    
    def add_test_data(self) -> bool:
        """Добавление тестовых данных"""
        print("🧪 Добавление тестовых данных...")
        
        test_users = [
            {"vk_user_id": 1001, "first_name": "Анна", "last_name": "Иванова", "age": 25, "sex": 1, "city": "Москва"},
            {"vk_user_id": 1002, "first_name": "Петр", "last_name": "Петров", "age": 30, "sex": 2, "city": "СПб"},
            {"vk_user_id": 1003, "first_name": "Мария", "last_name": "Сидорова", "age": 28, "sex": 1, "city": "Казань"},
        ]
        
        success_count = 0
        for user_data in test_users:
            if self.db_interface.add_user(**user_data):
                success_count += 1
                print(f"  ✅ Пользователь {user_data['vk_user_id']} добавлен")
            else:
                print(f"  ❌ Ошибка добавления пользователя {user_data['vk_user_id']}")
        
        # Добавляем тестовые логи
        test_logs = [
            {"vk_user_id": 0, "log_level": "info", "log_message": "Система запущена"},
            {"vk_user_id": 0, "log_level": "debug", "log_message": "Инициализация базы данных"},
            {"vk_user_id": 1001, "log_level": "info", "log_message": "Пользователь зашел в бота"},
        ]
        
        for log_data in test_logs:
            if self.db_interface.add_bot_log(**log_data):
                print(f"  ✅ Лог добавлен: {log_data['log_message']}")
            else:
                print(f"  ❌ Ошибка добавления лога")
        
        # Добавляем тестовые сообщения
        test_messages = [
            {"vk_user_id": 1001, "message_type": "command", "message_text": "/start"},
            {"vk_user_id": 1001, "message_type": "response", "message_text": "Привет! Добро пожаловать в VKinder Bot!"},
            {"vk_user_id": 1002, "message_type": "command", "message_text": "/help"},
        ]
        
        for msg_data in test_messages:
            if self.db_interface.add_bot_message(**msg_data):
                print(f"  ✅ Сообщение добавлено: {msg_data['message_text']}")
            else:
                print(f"  ❌ Ошибка добавления сообщения")
        
        print(f"\n✅ Тестовые данные добавлены: {success_count}/{len(test_users)} пользователей")
        return True
    
    def show_logs(self, user_id: Optional[int] = None, level: Optional[str] = None, limit: int = 20) -> None:
        """Показать логи"""
        print(f"📋 Логи бота (лимит: {limit}):")
        if user_id:
            print(f"  Пользователь: {user_id}")
        if level:
            print(f"  Уровень: {level}")
        print("=" * 50)
        
        logs = self.db_interface.get_bot_logs(vk_user_id=user_id or 0, log_level=level, limit=limit)
        
        if not logs:
            print("📭 Логов не найдено")
            return
        
        for log in logs:
            user_info = f"Пользователь {log['vk_user_id']}" if log['vk_user_id'] != 0 else "Система"
            print(f"  [{log['log_level'].upper()}] {user_info}: {log['log_message']}")
            print(f"    Время: {log['created_at']}")
            print()
    
    def show_messages(self, user_id: int, limit: int = 20) -> None:
        """Показать сообщения пользователя"""
        print(f"💬 Сообщения пользователя {user_id} (лимит: {limit}):")
        print("=" * 50)
        
        messages = self.db_interface.get_user_messages(vk_user_id=user_id, limit=limit)
        
        if not messages:
            print("📭 Сообщений не найдено")
            return
        
        for msg in messages:
            print(f"  [{msg['message_type'].upper()}] {msg['message_text']}")
            print(f"    Время: {msg['sent_at']}")
            print()
    
    def show_favorites(self, user_id: int) -> None:
        """Показать избранных пользователя"""
        print(f"❤️ Избранные пользователя {user_id}:")
        print("=" * 50)
        
        favorites = self.db_interface.get_favorites(user_vk_id=user_id)
        
        if not favorites:
            print("📭 Избранных не найдено")
            return
        
        for fav in favorites:
            print(f"  ID: {fav['favorite_vk_id']}")
            print(f"    Добавлен: {fav['created_at']}")
            print()
    
    # === КОМАНДЫ POSTGRESQL ===
    
    def start_postgresql(self) -> None:
        """Запуск PostgreSQL (универсальный для всех ОС)"""
        print("🚀 Запуск PostgreSQL...")
        if self.postgres_manager.start_postgresql():
            print("✅ PostgreSQL запущен успешно")
        else:
            print("❌ Ошибка запуска PostgreSQL")
    
    def stop_postgresql(self) -> None:
        """Остановка PostgreSQL (универсальный для всех ОС)"""
        print("🛑 Остановка PostgreSQL...")
        if self.postgres_manager.stop_postgresql():
            print("✅ PostgreSQL остановлен успешно")
        else:
            print("❌ Ошибка остановки PostgreSQL")
    
    def restart_postgresql(self) -> None:
        """Перезапуск PostgreSQL (универсальный для всех ОС)"""
        print("🔄 Перезапуск PostgreSQL...")
        if self.postgres_manager.restart_postgresql():
            print("✅ PostgreSQL перезапущен успешно")
        else:
            print("❌ Ошибка перезапуска PostgreSQL")
    
    def check_postgresql_status(self) -> None:
        """Проверка статуса PostgreSQL"""
        print("🔍 Проверка статуса PostgreSQL...")
        if self.postgres_manager.check_postgresql_status():
            print("✅ PostgreSQL запущен и доступен")
        else:
            print("❌ PostgreSQL не запущен или недоступен")
    
    def show_postgresql_info(self) -> None:
        """Показать информацию о PostgreSQL"""
        print("📊 Информация о PostgreSQL:")
        print("=" * 50)
        
        info = self.postgres_manager.get_postgresql_info()
        if 'error' not in info:
            print(f"🐘 Версия: {info['version']}")
            print(f"🏠 Хост: {info['host']}:{info['port']}")
            print(f"👤 Пользователь: {info['user']}")
            print(f"📄 Целевая БД: {info['target_database']}")
            print(f"✅ БД существует: {info['target_database_exists']}")
            print(f"📋 Всего БД: {len(info['databases'])}")
            print("\n📋 Список баз данных:")
            for db in info['databases']:
                print(f"  📄 {db}")
        else:
            print(f"❌ Ошибка получения информации: {info['error']}")


def main():
    """Основная функция CLI"""
    parser = argparse.ArgumentParser(description="CLI для управления базой данных VKinder Bot")
    
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")
    
    # Команда создания базы
    subparsers.add_parser("create", help="Создать все таблицы базы данных")
    
    # Команда удаления базы
    subparsers.add_parser("drop", help="Удалить все таблицы базы данных")
    
    # Команда очистки таблицы
    clear_parser = subparsers.add_parser("clear", help="Очистить таблицу")
    clear_parser.add_argument("table", help="Название таблицы для очистки")
    
    # Команда очистки всех таблиц
    subparsers.add_parser("clear-all", help="Очистить все таблицы")
    
    # Команда показа информации
    subparsers.add_parser("info", help="Показать информацию о базе данных")
    
    # Команда добавления тестовых данных
    subparsers.add_parser("test-data", help="Добавить тестовые данные")
    
    # Команда показа логов
    logs_parser = subparsers.add_parser("logs", help="Показать логи")
    logs_parser.add_argument("--user", type=int, help="ID пользователя")
    logs_parser.add_argument("--level", help="Уровень логирования")
    logs_parser.add_argument("--limit", type=int, default=20, help="Лимит записей")
    
    # Команда показа сообщений
    messages_parser = subparsers.add_parser("messages", help="Показать сообщения пользователя")
    messages_parser.add_argument("user_id", type=int, help="ID пользователя")
    messages_parser.add_argument("--limit", type=int, default=20, help="Лимит записей")
    
    # Команда показа избранных
    favorites_parser = subparsers.add_parser("favorites", help="Показать избранных пользователя")
    favorites_parser.add_argument("user_id", type=int, help="ID пользователя")
    
    # Команды PostgreSQL
    subparsers.add_parser("postgres-start", help="Запустить PostgreSQL")
    subparsers.add_parser("postgres-stop", help="Остановить PostgreSQL")
    subparsers.add_parser("postgres-restart", help="Перезапустить PostgreSQL")
    subparsers.add_parser("postgres-status", help="Проверить статус PostgreSQL")
    subparsers.add_parser("postgres-info", help="Показать информацию о PostgreSQL")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Создаем экземпляр CLI
    cli = DatabaseCLI()
    
    # Выполняем команду
    try:
        if args.command == "create":
            cli.create_database()
        elif args.command == "drop":
            cli.drop_database()
        elif args.command == "clear":
            cli.clear_table(args.table)
        elif args.command == "clear-all":
            cli.clear_all_tables()
        elif args.command == "info":
            cli.show_info()
        elif args.command == "test-data":
            cli.add_test_data()
        elif args.command == "logs":
            cli.show_logs(user_id=args.user, level=args.level, limit=args.limit)
        elif args.command == "messages":
            cli.show_messages(user_id=args.user_id, limit=args.limit)
        elif args.command == "favorites":
            cli.show_favorites(user_id=args.user_id)
        elif args.command == "postgres-start":
            cli.start_postgresql()
        elif args.command == "postgres-stop":
            cli.stop_postgresql()
        elif args.command == "postgres-restart":
            cli.restart_postgresql()
        elif args.command == "postgres-status":
            cli.check_postgresql_status()
        elif args.command == "postgres-info":
            cli.show_postgresql_info()
        else:
            print(f"❌ Неизвестная команда: {args.command}")
            
    except Exception as e:
        print(f"❌ Ошибка выполнения команды: {e}")


if __name__ == "__main__":
    main()
