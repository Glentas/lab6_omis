from enum import Enum
from pathlib import Path
import os


class AppConfig:
    """Конфигурация приложения"""
    
    # Пути
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    UPLOAD_DIR = DATA_DIR / "uploads"
    REPORTS_DIR = DATA_DIR / "reports"
    
    # Настройки
    SUPPORTED_FORMATS = [".pdf", ".docx", ".doc", ".txt", ".rtf"]
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Настройки анализа
    SIMILARITY_THRESHOLD = 0.8  # Порог совпадения
    MIN_MATCH_LENGTH = 20  # Минимальная длина совпадения
    
    # Инициализация директорий
    @classmethod
    def init_directories(cls):
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.UPLOAD_DIR.mkdir(exist_ok=True)
        cls.REPORTS_DIR.mkdir(exist_ok=True)


# Инициализация директорий при импорте
AppConfig.init_directories()
