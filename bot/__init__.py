"""
RuTracker Telegram Bot Package

This package contains all modules for the RuTracker Telegram Bot.
"""

__version__ = "1.0.0"
__author__ = "BigGratz"

# Экспортируем основные модули для удобного импорта
from bot.config import config
from bot.database import init_db, async_session, Game, Settings
from bot.parser import RutrackerParser
from bot.utils import *

__all__ = [
    'config',
    'init_db', 
    'async_session',
    'Game',
    'Settings',
    'RutrackerParser'
]
