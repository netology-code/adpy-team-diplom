#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для просмотра логов базы данных VKinder Bot
"""

import os
import sys
import glob
from datetime import datetime

def show_database_logs():
    """Показать доступные логи базы данных"""
    logs_dir = 'logs'
    
    if not os.path.exists(logs_dir):
        print("❌ Папка logs не найдена!")
        return
    
    print("📋 Доступные логи базы данных:")
    print("=" * 40)
    
    # Ищем файлы логов базы данных с временными метками
    log_patterns = [
        ('database_debug*.log', 'DEBUG', 'Отладочная информация базы данных')
    ]
    
    for pattern, level, description in log_patterns:
        files = glob.glob(os.path.join(logs_dir, pattern))
        if files:
            # Сортируем по времени модификации (новые сначала)
            files.sort(key=os.path.getmtime, reverse=True)
            for filepath in files:
                filename = os.path.basename(filepath)
                size = os.path.getsize(filepath)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                print(f"✅ {filename} ({level}) - {size} байт")
                print(f"   {description}")
                print(f"   Время модификации: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
        else:
            print(f"❌ {pattern} ({level}) - файлы не найдены")
            print()

def view_database_log_file(filename: str, lines: int = 50):
    """Просмотр содержимого файла лога базы данных"""
    logs_dir = 'logs'
    
    # Если filename содержит *, ищем по паттерну
    if '*' in filename:
        files = glob.glob(os.path.join(logs_dir, filename))
        if not files:
            print(f"❌ Файлы по паттерну {filename} не найдены!")
            return
        
        # Берем самый новый файл
        files.sort(key=os.path.getmtime, reverse=True)
        filepath = files[0]
        actual_filename = os.path.basename(filepath)
        print(f"📄 Найден файл: {actual_filename}")
    else:
        filepath = os.path.join(logs_dir, filename)
        if not os.path.exists(filepath):
            print(f"❌ Файл {filename} не найден!")
            return
    
    print(f"📄 Последние {lines} строк из {filename}:")
    print("=" * 60)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            
        # Показываем последние N строк
        start_line = max(0, len(all_lines) - lines)
        for line in all_lines[start_line:]:
            print(line.rstrip())
            
    except Exception as e:
        print(f"❌ Ошибка при чтении файла: {e}")

def view_realtime_database_logs():
    """Просмотр логов базы данных в реальном времени"""
    print("🔄 Просмотр логов базы данных в реальном времени (Ctrl+C для выхода)")
    print("=" * 60)
    
    try:
        import subprocess
        
        # Ищем самый новый файл database_debug с временной меткой
        log_files = glob.glob('logs/database_debug*.log')
        if log_files:
            log_files.sort(key=os.path.getmtime, reverse=True)
            log_file = log_files[0]
            print(f"📄 Просматриваем файл: {os.path.basename(log_file)}")
            subprocess.run(['tail', '-f', log_file])
        else:
            print("❌ Файлы логов базы данных не найдены!")
    except KeyboardInterrupt:
        print("\n⏹️  Просмотр логов остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def main():
    """Главная функция"""
    print("📊 VKinder Bot - Просмотр логов базы данных")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'debug':
            view_database_log_file('database_debug*.log', 50)
        elif command == 'follow':
            view_realtime_database_logs()
        else:
            print(f"❌ Неизвестная команда: {command}")
            print("Доступные команды: debug, follow")
    else:
        show_database_logs()
        print("💡 Использование:")
        print("   python view_logs.py debug   - показать DEBUG логи базы данных")
        print("   python view_logs.py follow  - следить за логами базы данных в реальном времени")

if __name__ == "__main__":
    main()