from datetime import datetime
from typing import Dict, Optional
from config import Config


class UserSession:
    """Класс для управления сессией пользователя"""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.tax_rate: float = Config.DEFAULT_TAX_RATE
        self.main_df = None
        self.final_df = None
        self.created_at = datetime.now()
        self.last_activity = datetime.now()

    def update_activity(self):
        """Обновление времени последней активности"""
        self.last_activity = datetime.now()

    def is_expired(self, hours: int = 24) -> bool:
        """Проверка истечения срока сессии"""
        return (datetime.now() - self.last_activity).total_seconds() > hours * 3600


class SessionManager:
    """Менеджер сессий пользователей"""

    def __init__(self):
        self.sessions: Dict[int, UserSession] = {}

    def get_session(self, user_id: int) -> UserSession:
        """Получение или создание сессии пользователя"""
        if user_id not in self.sessions or self.sessions[user_id].is_expired():
            self.sessions[user_id] = UserSession(user_id)
        return self.sessions[user_id]

    def cleanup_expired(self):
        """Очистка просроченных сессий"""
        expired_users = [
            user_id
            for user_id, session in self.sessions.items()
            if session.is_expired()
        ]
        for user_id in expired_users:
            del self.sessions[user_id]
        return len(expired_users)


# Глобальный экземпляр менеджера сессий
session_manager = SessionManager()
