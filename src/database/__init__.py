"""
Пакет для работы с базой данных VKinder Bot

Содержит:
- models.py - SQLAlchemy модели
- database_interface.py - основной интерфейс БД
- db_api.py - API функции
- db_cli.py - CLI инструменты
- postgres_manager.py - менеджер PostgreSQL
"""

from .database_interface import DatabaseInterface
from .db_api import *
from .models import *

__all__ = [
    'DatabaseInterface',
    # API функции экспортируются через db_api
]
