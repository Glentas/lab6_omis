import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, TypeVar, Generic
from datetime import datetime
import uuid

T = TypeVar('T')

class JSONStorage(Generic[T]):
    """Простое JSON-хранилище для MVP"""
    
    def __init__(self, storage_path: str = "data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
    
    def _get_file_path(self, collection: str) -> Path:
        return self.storage_path / f"{collection}.json"
    
    def load_collection(self, collection: str) -> Dict[str, Any]:
        file_path = self._get_file_path(collection)
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def save_collection(self, collection: str, data: Dict[str, Any]):
        file_path = self._get_file_path(collection)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def create(self, collection: str, item: T, item_id: Optional[str] = None) -> str:
        data = self.load_collection(collection)
        
        if item_id is None:
            item_id = str(uuid.uuid4())
        
        if hasattr(item, 'dict'):
            data[item_id] = item.dict()
        else:
            data[item_id] = item
        
        self.save_collection(collection, data)
        return item_id
    
    def read(self, collection: str, item_id: str) -> Optional[Dict[str, Any]]:
        data = self.load_collection(collection)
        return data.get(item_id)
    
    def read_all(self, collection: str) -> List[Dict[str, Any]]:
        data = self.load_collection(collection)
        return list(data.values())
    
    def update(self, collection: str, item_id: str, updates: Dict[str, Any]):
        data = self.load_collection(collection)
        if item_id in data:
            data[item_id].update(updates)
            self.save_collection(collection, data)
    
    def delete(self, collection: str, item_id: str):
        data = self.load_collection(collection)
        if item_id in data:
            del data[item_id]
            self.save_collection(collection, data)
    
    def find(self, collection: str, **filters) -> List[Dict[str, Any]]:
        data = self.load_collection(collection)
        results = []
        
        for item in data.values():
            match = True
            for key, value in filters.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                results.append(item)
        
        return results


class StorageManager:
    """Менеджер хранилища для всех сущностей"""
    
    def __init__(self):
        self.users = JSONStorage("users")
        self.documents = JSONStorage("documents")
        self.processed_texts = JSONStorage("processed_texts")
        self.checks = JSONStorage("checks")
        self.results = JSONStorage("results")
        self.reports = JSONStorage("reports")
        self.sessions = JSONStorage("sessions")
        self.sources = JSONStorage("sources")
        
        # Инициализация тестовых данных
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Инициализация тестовых данных"""
        if not self.users.load_collection("users"):
            # Создаем тестового администратора
            admin_user = {
                "user_id": "admin_001",
                "name": "Администратор системы",
                "email": "admin@system.ru",
                "role": "admin",
                "registration_date": datetime.now().isoformat()
            }
            self.users.create("users", admin_user, "admin_001")
            
            # Создаем тестового преподавателя
            teacher_user = {
                "user_id": "teacher_001",
                "name": "Преподаватель Иванов",
                "email": "teacher@university.ru",
                "role": "teacher",
                "registration_date": datetime.now().isoformat()
            }
            self.users.create("users", teacher_user, "teacher_001")
            
            # Создаем тестового студента
            student_user = {
                "user_id": "student_001",
                "name": "Студент Петров",
                "email": "student@university.ru",
                "role": "student",
                "registration_date": datetime.now().isoformat()
            }
            self.users.create("users", student_user, "student_001")
        
        # Инициализация тестовых источников
        if not self.sources.load_collection("sources"):
            sample_sources = [
                {
                    "source_id": "source_001",
                    "source_name": "Введение в алгоритмы",
                    "author": "Томас Кормен",
                    "url": "https://example.com/algorithms",
                    "category": "book"
                },
                {
                    "source_id": "source_002",
                    "source_name": "Машинное обучение: основы",
                    "author": "Кевин Мерфи",
                    "url": "https://example.com/ml",
                    "category": "book"
                },
                {
                    "source_id": "source_003",
                    "source_name": "Паттерны проектирования",
                    "author": "Эрик Гамма",
                    "url": "https://example.com/patterns",
                    "category": "book"
                }
            ]
            
            for source in sample_sources:
                self.sources.create("sources", source, source["source_id"])
