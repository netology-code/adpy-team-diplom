#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка безопасности проекта
"""

import os
import re
import subprocess

def check_gitignore():
    """Проверка .gitignore на наличие всех необходимых исключений"""
    print("🔍 Проверка .gitignore...")
    
    required_patterns = [
        '.env',
        'user_token.txt',
        'logs/',
        '*.token',
        '*.key',
        'secrets.json',
        'credentials.json'
    ]
    
    try:
        with open('.gitignore', 'r', encoding='utf-8') as f:
            gitignore_content = f.read()
        
        missing_patterns = []
        for pattern in required_patterns:
            if pattern not in gitignore_content:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            print(f"❌ Отсутствуют паттерны в .gitignore: {missing_patterns}")
            return False
        else:
            print("✅ .gitignore содержит все необходимые исключения")
            return True
            
    except FileNotFoundError:
        print("❌ Файл .gitignore не найден")
        return False

def check_tokens_in_code():
    """Проверка наличия токенов в коде"""
    print("\n🔍 Проверка кода на наличие токенов...")
    
    # Паттерны для поиска токенов
    token_patterns = [
        r'vk1\.a\.[A-Za-z0-9_-]{40,}',  # VK токены (минимум 40 символов)
        r'[A-Za-z0-9]{50,}',            # Очень длинные строки (возможные токены)
        r'[A-Za-z0-9]{40,}',            # Длинные строки
    ]
    
    # Файлы для проверки
    files_to_check = [
        'src/bot/vk_bot.py',
        'src/config/setup_env.py',
        'src/token/setup_user_token.py',
        'src/token/get_token_manual.py',
        'main.py'
    ]
    
    found_tokens = []
    
    for filename in files_to_check:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern in token_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # Исключаем placeholder значения и известные классы
                        exclude_patterns = [
                            'your_', 'placeholder', 'example', 'here',
                            'botdatabaseintegration', 'databaseinterface', 
                            'postgresqlmanager', 'vkinderbot', 'botsettings',
                            'tokenmanager', 'vkbotlongpoll', 'vkkeyboard',
                            'vkkeyboardcolor', 'vkboteventtype'
                        ]
                        if not any(pattern in match.lower() for pattern in exclude_patterns):
                            found_tokens.append((filename, match))
                            
            except Exception as e:
                print(f"⚠️  Ошибка при чтении {filename}: {e}")
    
    if found_tokens:
        print("❌ Найдены возможные токены в коде:")
        for filename, token in found_tokens:
            print(f"   {filename}: {token[:20]}...")
        return False
    else:
        print("✅ Токены в коде не найдены")
        return True

def check_git_status():
    """Проверка статуса Git на наличие секретных файлов"""
    print("\n🔍 Проверка статуса Git...")
    
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        # Проверяем, есть ли секретные файлы в staging area
        secret_files = ['.env', 'user_token.txt', 'logs/', '*.token', '*.key']
        
        for line in result.stdout.split('\n'):
            if line.strip():
                for secret_file in secret_files:
                    if secret_file in line:
                        print(f"❌ Секретный файл в Git: {line.strip()}")
                        return False
        
        print("✅ Секретные файлы не найдены в Git")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Ошибка при проверке Git: {e}")
        return False

def main():
    """Главная функция проверки безопасности"""
    print("🛡️  Проверка безопасности VKinder Bot")
    print("=" * 50)
    
    checks = [
        check_gitignore,
        check_tokens_in_code,
        check_git_status
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
        print()
    
    print("=" * 50)
    if passed == total:
        print("🎉 Все проверки безопасности пройдены!")
        print("✅ Репозиторий безопасен для публикации")
    else:
        print(f"⚠️  Пройдено {passed}/{total} проверок")
        print("❌ Требуется исправление проблем безопасности")
    
    return passed == total

if __name__ == "__main__":
    main()
