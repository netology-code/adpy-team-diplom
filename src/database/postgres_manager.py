#!/usr/bin/env python3
"""
Менеджер PostgreSQL для автоматической проверки и запуска базы данных
Проверяет статус PostgreSQL и запускает его при необходимости
"""

import os
import sys
import subprocess
import time
import platform
import psycopg2
from typing import Optional, Dict, Any
from loguru import logger


class PostgreSQLManager:
    """Менеджер для управления PostgreSQL"""
    
    def __init__(self):
        """Инициализация менеджера PostgreSQL"""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '5432'))
        self.database = os.getenv('DB_NAME', 'vkinder_db')
        self.user = os.getenv('DB_USER', 'vkinder_user')
        self.password = os.getenv('DB_PASSWORD', 'vkinder123')
        self.os_type = self._detect_os()
    
    def _detect_os(self) -> str:
        """
        Определение операционной системы
        
        Returns:
            str: 'windows', 'macos', 'linux' или 'unknown'
        """
        system = platform.system().lower()
        if system == 'windows':
            return 'windows'
        elif system == 'darwin':
            return 'macos'
        elif system == 'linux':
            return 'linux'
        else:
            return 'unknown'
    
    def check_postgresql_status(self) -> bool:
        """
        Проверка статуса PostgreSQL
        
        Returns:
            bool: True если PostgreSQL запущен, False иначе
        """
        try:
            # Пробуем подключиться к PostgreSQL
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database='postgres',  # Подключаемся к системной БД
                user=self.user,
                password=self.password
            )
            conn.close()
            logger.info("✅ PostgreSQL запущен и доступен")
            return True
            
        except psycopg2.OperationalError as e:
            logger.warning(f"⚠️ PostgreSQL недоступен: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка проверки PostgreSQL: {e}")
            return False
    
    def start_postgresql(self) -> bool:
        """
        Универсальный запуск PostgreSQL для всех ОС
        
        Returns:
            bool: True если запуск успешен, False иначе
        """
        try:
            logger.info(f"🚀 Запуск PostgreSQL на {self.os_type.upper()}...")
            
            if self.os_type == 'windows':
                return self._start_postgresql_windows()
            elif self.os_type == 'macos':
                return self._start_postgresql_macos()
            elif self.os_type == 'linux':
                return self._start_postgresql_linux()
            else:
                logger.error(f"❌ Неподдерживаемая ОС: {self.os_type}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка запуска PostgreSQL: {e}")
            return False
    
    def _start_postgresql_windows(self) -> bool:
        """
        Запуск PostgreSQL на Windows
        
        Returns:
            bool: True если запуск успешен, False иначе
        """
        try:
            logger.info("🚀 Запуск PostgreSQL на Windows...")
            
            # Проверяем службу PostgreSQL
            if self._check_windows_service():
                return self._start_windows_service()
            
            # Проверяем установку через установщик
            elif self._check_windows_installation():
                return self._start_windows_postgres()
            
            else:
                logger.error("❌ PostgreSQL не найден. Установите PostgreSQL с официального сайта")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка запуска PostgreSQL на Windows: {e}")
            return False
    
    def _start_postgresql_linux(self) -> bool:
        """
        Запуск PostgreSQL на Linux
        
        Returns:
            bool: True если запуск успешен, False иначе
        """
        try:
            logger.info("🚀 Запуск PostgreSQL на Linux...")
            
            # Проверяем systemd
            if self._check_systemd():
                return self._start_systemd_postgres()
            
            # Проверяем service
            elif self._check_service_command():
                return self._start_service_postgres()
            
            # Проверяем pg_ctl
            elif self._check_pg_ctl():
                return self._start_pg_ctl()
            
            else:
                logger.error("❌ PostgreSQL не найден. Установите: sudo apt install postgresql")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка запуска PostgreSQL на Linux: {e}")
            return False
    
    def _check_windows_service(self) -> bool:
        """Проверка службы PostgreSQL на Windows"""
        try:
            result = subprocess.run(['sc', 'query', 'postgresql'], 
                                  capture_output=True, text=True, timeout=10)
            return 'postgresql' in result.stdout.lower()
        except:
            return False
    
    def _start_windows_service(self) -> bool:
        """Запуск службы PostgreSQL на Windows"""
        try:
            result = subprocess.run(['sc', 'start', 'postgresql'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                logger.info("✅ Служба PostgreSQL запущена")
                return True
            else:
                logger.error(f"❌ Ошибка запуска службы: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка запуска службы: {e}")
            return False
    
    def _check_windows_installation(self) -> bool:
        """Проверка установки PostgreSQL на Windows"""
        try:
            # Проверяем стандартные пути установки
            common_paths = [
                r"C:\Program Files\PostgreSQL",
                r"C:\Program Files (x86)\PostgreSQL",
                r"C:\PostgreSQL"
            ]
            for path in common_paths:
                if os.path.exists(path):
                    return True
            return False
        except:
            return False
    
    def _start_windows_postgres(self) -> bool:
        """Запуск PostgreSQL через pg_ctl на Windows"""
        try:
            # Ищем pg_ctl в стандартных путях
            pg_ctl_paths = [
                r"C:\Program Files\PostgreSQL\*\bin\pg_ctl.exe",
                r"C:\Program Files (x86)\PostgreSQL\*\bin\pg_ctl.exe"
            ]
            
            for path_pattern in pg_ctl_paths:
                import glob
                matches = glob.glob(path_pattern)
                if matches:
                    pg_ctl = matches[0]
                    result = subprocess.run([pg_ctl, 'start', '-D', 'data'], 
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        logger.info("✅ PostgreSQL запущен через pg_ctl")
                        return True
            
            logger.error("❌ Не удалось найти pg_ctl")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка запуска PostgreSQL: {e}")
            return False
    
    def _check_systemd(self) -> bool:
        """Проверка systemd на Linux"""
        try:
            result = subprocess.run(['systemctl', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _start_systemd_postgres(self) -> bool:
        """Запуск PostgreSQL через systemd"""
        try:
            result = subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                logger.info("✅ PostgreSQL запущен через systemctl")
                return True
            else:
                logger.error(f"❌ Ошибка запуска через systemctl: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка запуска через systemctl: {e}")
            return False
    
    def _check_service_command(self) -> bool:
        """Проверка команды service на Linux"""
        try:
            result = subprocess.run(['service', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _start_service_postgres(self) -> bool:
        """Запуск PostgreSQL через service"""
        try:
            result = subprocess.run(['sudo', 'service', 'postgresql', 'start'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                logger.info("✅ PostgreSQL запущен через service")
                return True
            else:
                logger.error(f"❌ Ошибка запуска через service: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка запуска через service: {e}")
            return False
    
    def _check_pg_ctl(self) -> bool:
        """Проверка pg_ctl на Linux"""
        try:
            result = subprocess.run(['which', 'pg_ctl'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _start_pg_ctl(self) -> bool:
        """Запуск PostgreSQL через pg_ctl на Linux"""
        try:
            # Ищем директорию данных PostgreSQL
            data_dirs = [
                '/var/lib/postgresql/data',
                '/usr/local/var/postgres',
                '/opt/postgresql/data'
            ]
            
            for data_dir in data_dirs:
                if os.path.exists(data_dir):
                    result = subprocess.run(['pg_ctl', 'start', '-D', data_dir], 
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        logger.info("✅ PostgreSQL запущен через pg_ctl")
                        return True
            
            logger.error("❌ Не удалось найти директорию данных PostgreSQL")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка запуска через pg_ctl: {e}")
            return False
    
    def start_postgresql_macos(self) -> bool:
        """
        Запуск PostgreSQL на macOS
        
        Returns:
            bool: True если запуск успешен, False иначе
        """
        try:
            logger.info("🚀 Запуск PostgreSQL на macOS...")
            
            # Проверяем, установлен ли PostgreSQL через Homebrew
            if self._check_homebrew_postgres():
                return self._start_homebrew_postgres()
            
            # Проверяем системный PostgreSQL
            elif self._check_system_postgres():
                return self._start_system_postgres()
            
            else:
                logger.error("❌ PostgreSQL не найден. Установите через Homebrew: brew install postgresql")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка запуска PostgreSQL: {e}")
            return False
    
    def _check_homebrew_postgres(self) -> bool:
        """Проверка наличия PostgreSQL через Homebrew"""
        try:
            result = subprocess.run(['brew', 'services', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            return 'postgresql' in result.stdout
        except:
            return False
    
    def _check_system_postgres(self) -> bool:
        """Проверка системного PostgreSQL"""
        try:
            result = subprocess.run(['which', 'postgres'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _start_homebrew_postgres(self) -> bool:
        """Запуск PostgreSQL через Homebrew"""
        try:
            logger.info("🍺 Запуск PostgreSQL через Homebrew...")
            
            # Запускаем PostgreSQL через brew services
            result = subprocess.run(['brew', 'services', 'start', 'postgresql'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("✅ PostgreSQL запущен через Homebrew")
                return True
            else:
                logger.error(f"❌ Ошибка запуска через Homebrew: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Таймаут запуска PostgreSQL")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка запуска через Homebrew: {e}")
            return False
    
    def _start_system_postgres(self) -> bool:
        """Запуск системного PostgreSQL"""
        try:
            logger.info("🔧 Запуск системного PostgreSQL...")
            
            # Пробуем запустить через pg_ctl
            result = subprocess.run(['pg_ctl', 'start', '-D', '/usr/local/var/postgres'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("✅ Системный PostgreSQL запущен")
                return True
            else:
                logger.error(f"❌ Ошибка запуска системного PostgreSQL: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Таймаут запуска PostgreSQL")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка запуска системного PostgreSQL: {e}")
            return False
    
    def wait_for_postgresql(self, timeout: int = 60) -> bool:
        """
        Ожидание запуска PostgreSQL
        
        Args:
            timeout (int): Таймаут ожидания в секундах
            
        Returns:
            bool: True если PostgreSQL запустился, False иначе
        """
        logger.info(f"⏳ Ожидание запуска PostgreSQL (таймаут: {timeout}с)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_postgresql_status():
                logger.info("✅ PostgreSQL успешно запущен!")
                return True
            
            time.sleep(2)  # Ждем 2 секунды между проверками
        
        logger.error(f"❌ Таймаут ожидания PostgreSQL ({timeout}с)")
        return False
    
    def ensure_postgresql_running(self) -> bool:
        """
        Гарантирует, что PostgreSQL запущен
        
        Returns:
            bool: True если PostgreSQL запущен, False иначе
        """
        logger.info("🔍 Проверка статуса PostgreSQL...")
        
        # Проверяем текущий статус
        if self.check_postgresql_status():
            return True
        
        # Если не запущен, пытаемся запустить
        logger.info("🚀 PostgreSQL не запущен, пытаемся запустить...")
        
        if self.start_postgresql():
            # Ждем запуска
            if self.wait_for_postgresql():
                return True
        
        logger.error("❌ Не удалось запустить PostgreSQL")
        return False
    
    def create_database_if_not_exists(self) -> bool:
        """
        Создание базы данных если она не существует
        
        Returns:
            bool: True если БД создана или существует, False иначе
        """
        try:
            # Подключаемся к системной БД postgres
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database='postgres',
                user=self.user,
                password=self.password
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Проверяем, существует ли БД
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.database,))
            if cursor.fetchone():
                logger.info(f"✅ База данных '{self.database}' уже существует")
                cursor.close()
                conn.close()
                return True
            
            # Создаем БД
            logger.info(f"🔨 Создание базы данных '{self.database}'...")
            cursor.execute(f'CREATE DATABASE "{self.database}"')
            logger.info(f"✅ База данных '{self.database}' создана")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания базы данных: {e}")
            return False
    
    def get_postgresql_info(self) -> Dict[str, Any]:
        """
        Получение информации о PostgreSQL
        
        Returns:
            Dict[str, Any]: Информация о PostgreSQL
        """
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database='postgres',
                user=self.user,
                password=self.password
            )
            cursor = conn.cursor()
            
            # Получаем версию PostgreSQL
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            
            # Получаем список БД
            cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
            databases = [row[0] for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            return {
                'version': version,
                'host': self.host,
                'port': self.port,
                'user': self.user,
                'databases': databases,
                'target_database': self.database,
                'target_database_exists': self.database in databases
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации о PostgreSQL: {e}")
            return {'error': str(e)}
    
    def stop_postgresql(self) -> bool:
        """
        Универсальная остановка PostgreSQL для всех ОС
        
        Returns:
            bool: True если остановка успешна, False иначе
        """
        try:
            logger.info(f"🛑 Остановка PostgreSQL на {self.os_type.upper()}...")
            
            if self.os_type == 'windows':
                return self._stop_postgresql_windows()
            elif self.os_type == 'macos':
                return self._stop_postgresql_macos()
            elif self.os_type == 'linux':
                return self._stop_postgresql_linux()
            else:
                logger.error(f"❌ Неподдерживаемая ОС: {self.os_type}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка остановки PostgreSQL: {e}")
            return False
    
    def _stop_postgresql_windows(self) -> bool:
        """Остановка PostgreSQL на Windows"""
        try:
            # Пытаемся остановить службу
            result = subprocess.run(['sc', 'stop', 'postgresql'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                logger.info("✅ Служба PostgreSQL остановлена")
                return True
            else:
                logger.error(f"❌ Ошибка остановки службы: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка остановки PostgreSQL на Windows: {e}")
            return False
    
    def _stop_postgresql_linux(self) -> bool:
        """Остановка PostgreSQL на Linux"""
        try:
            # Пытаемся остановить через systemctl
            if self._check_systemd():
                result = subprocess.run(['sudo', 'systemctl', 'stop', 'postgresql'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    logger.info("✅ PostgreSQL остановлен через systemctl")
                    return True
            
            # Пытаемся остановить через service
            if self._check_service_command():
                result = subprocess.run(['sudo', 'service', 'postgresql', 'stop'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    logger.info("✅ PostgreSQL остановлен через service")
                    return True
            
            logger.error("❌ Не удалось остановить PostgreSQL")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка остановки PostgreSQL на Linux: {e}")
            return False
    
    def _stop_postgresql_macos(self) -> bool:
        """Остановка PostgreSQL на macOS"""
        try:
            # Пытаемся остановить через Homebrew
            if self._check_homebrew_postgres():
                result = subprocess.run(['brew', 'services', 'stop', 'postgresql'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    logger.info("✅ PostgreSQL остановлен через Homebrew")
                    return True
            
            # Пытаемся остановить через pg_ctl
            if self._check_system_postgres():
                result = subprocess.run(['pg_ctl', 'stop'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    logger.info("✅ PostgreSQL остановлен через pg_ctl")
                    return True
            
            logger.error("❌ Не удалось остановить PostgreSQL")
            return False
        except Exception as e:
            logger.error(f"❌ Ошибка остановки PostgreSQL на macOS: {e}")
            return False
    
    def restart_postgresql(self) -> bool:
        """
        Универсальный перезапуск PostgreSQL для всех ОС
        
        Returns:
            bool: True если перезапуск успешен, False иначе
        """
        try:
            logger.info(f"🔄 Перезапуск PostgreSQL на {self.os_type.upper()}...")
            
            # Сначала останавливаем
            if self.stop_postgresql():
                time.sleep(2)  # Небольшая пауза
                
                # Затем запускаем
                if self.start_postgresql():
                    # Ждем запуска
                    if self.wait_for_postgresql():
                        logger.info("✅ PostgreSQL успешно перезапущен")
                        return True
            
            logger.error("❌ Не удалось перезапустить PostgreSQL")
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка перезапуска PostgreSQL: {e}")
            return False


def main():
    """Основная функция для тестирования менеджера PostgreSQL"""
    print("🐘 МЕНЕДЖЕР POSTGRESQL")
    print("=" * 50)
    
    manager = PostgreSQLManager()
    
    # Проверяем и запускаем PostgreSQL
    if manager.ensure_postgresql_running():
        print("✅ PostgreSQL запущен и доступен")
        
        # Создаем БД если нужно
        if manager.create_database_if_not_exists():
            print("✅ База данных готова")
        
        # Показываем информацию
        info = manager.get_postgresql_info()
        if 'error' not in info:
            print(f"\n📊 Информация о PostgreSQL:")
            print(f"  🐘 Версия: {info['version']}")
            print(f"  🏠 Хост: {info['host']}:{info['port']}")
            print(f"  👤 Пользователь: {info['user']}")
            print(f"  📄 База данных: {info['target_database']}")
            print(f"  ✅ БД существует: {info['target_database_exists']}")
            print(f"  📋 Всего БД: {len(info['databases'])}")
        else:
            print(f"❌ Ошибка получения информации: {info['error']}")
    else:
        print("❌ Не удалось запустить PostgreSQL")
        print("\n🔧 Рекомендации:")
        print("  1. Установите PostgreSQL: brew install postgresql")
        print("  2. Запустите вручную: brew services start postgresql")
        print("  3. Проверьте настройки в .env файле")


if __name__ == "__main__":
    main()
