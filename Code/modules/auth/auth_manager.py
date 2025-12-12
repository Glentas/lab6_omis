import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from app.storage.json_storage import StorageManager
from app.core.models import User, UserRole, Session


class AuthManager:
    """Менеджер аутентификации и авторизации"""
    
    def __init__(self, storage: StorageManager):
        self.storage = storage
    
    def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Вход в систему"""
        # В MVP используем email как пароль для демонстрации
        users = self.storage.users.find("users", email=email)
        if not users:
            return None
        
        user_data = users[0]
        
        # Создаем сессию
        session_id = str(uuid.uuid4())
        session_data = {
            "session_id": session_id,
            "user_id": user_data["user_id"],
            "login_time": datetime.now().isoformat(),
            "is_active": True
        }
        self.storage.sessions.create("sessions", session_data, session_id)
        
        return {
            "user": user_data,
            "session_id": session_id
        }
    
    def logout(self, session_id: str):
        """Выход из системы"""
        self.storage.sessions.update("sessions", session_id, {
            "logout_time": datetime.now().isoformat(),
            "is_active": False
        })
    
    def get_current_user(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение текущего пользователя по сессии"""
        session_data = self.storage.sessions.read("sessions", session_id)
        if not session_data or not session_data.get("is_active"):
            return None
        
        user_id = session_data.get("user_id")
        if not user_id:
            return None
        
        return self.storage.users.read("users", user_id)
    
    def has_permission(self, user: Dict[str, Any], required_role: UserRole) -> bool:
        """Проверка прав доступа"""
        user_role = UserRole(user.get("role", ""))
        
        # Иерархия ролей
        role_hierarchy = {
            UserRole.ADMIN: [UserRole.ADMIN, UserRole.TEACHER, UserRole.STUDENT],
            UserRole.TEACHER: [UserRole.TEACHER, UserRole.STUDENT],
            UserRole.STUDENT: [UserRole.STUDENT]
        }
        
        return required_role in role_hierarchy.get(user_role, [])
    
    def create_user(self, name: str, email: str, role: UserRole) -> str:
        """Создание нового пользователя (для администратора)"""
        user_id = str(uuid.uuid4())
        user_data = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "role": role.value,
            "registration_date": datetime.now().isoformat()
        }
        
        self.storage.users.create("users", user_data, user_id)
        return user_id
