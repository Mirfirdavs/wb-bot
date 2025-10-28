import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import pandas as pd

from config import Config
from .session_manager import session_manager
from utils.logger import logger


@dataclass
class UserStat:
    """Статистика пользователя"""

    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    sessions_count: int = 0
    files_processed: int = 0
    last_activity: Optional[datetime] = None
    created_at: Optional[datetime] = None


@dataclass
class BotStat:
    """Общая статистика бота"""

    total_users: int = 0
    active_today: int = 0
    total_files: int = 0
    memory_usage_mb: float = 0.0
    uptime_days: float = 0.0


class AdminManager:
    """Менеджер для админских функций"""

    def __init__(self):
        self.user_stats: Dict[int, UserStat] = {}
        self.bot_start_time = datetime.now()
        self.broadcast_messages: List[dict] = []

    def update_user_activity(
        self,
        user_id: int,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
    ):
        """Обновление активности пользователя"""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = UserStat(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=first_name,
                created_at=datetime.now(),
            )

        self.user_stats[user_id].sessions_count += 1
        self.user_stats[user_id].last_activity = datetime.now()

        # Обновляем имя, если изменилось
        if username:
            self.user_stats[user_id].username = username
        if first_name:
            self.user_stats[user_id].first_name = first_name
        if last_name:
            self.user_stats[user_id].last_name = last_name

    def record_file_processed(self, user_id: int):
        """Запись обработки файла"""
        if user_id in self.user_stats:
            self.user_stats[user_id].files_processed += 1

    def get_bot_stats(self) -> BotStat:
        """Получение общей статистики бота"""
        now = datetime.now()
        active_today = sum(
            1
            for stat in self.user_stats.values()
            if stat.last_activity and (now - stat.last_activity) < timedelta(days=1)
        )

        # Примерное использование памяти
        import psutil

        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB

        return BotStat(
            total_users=len(self.user_stats),
            active_today=active_today,
            total_files=sum(stat.files_processed for stat in self.user_stats.values()),
            memory_usage_mb=memory_usage,
            uptime_days=(now - self.bot_start_time).total_seconds() / 86400,
        )

    def get_user_stats_df(self) -> pd.DataFrame:
        """Получение статистики пользователей в виде DataFrame"""
        if not self.user_stats:
            return pd.DataFrame()

        data = []
        for stat in self.user_stats.values():
            data.append(
                {
                    "user_id": stat.user_id,
                    "username": f"@{stat.username}" if stat.username else "Нет",
                    "first_name": stat.first_name or "Нет",
                    "sessions": stat.sessions_count,
                    "files_processed": stat.files_processed,
                    "last_activity": stat.last_activity.strftime("%Y-%m-%d %H:%M")
                    if stat.last_activity
                    else "Нет данных",
                    "days_since_active": (datetime.now() - stat.last_activity).days
                    if stat.last_activity
                    else None,
                }
            )

        return pd.DataFrame(data)

    def get_top_users(self, limit: int = 10) -> List[UserStat]:
        """Топ пользователей по активности"""
        sorted_users = sorted(
            self.user_stats.values(), key=lambda x: x.files_processed, reverse=True
        )
        return sorted_users[:limit]

    async def send_broadcast_message(
        self, bot, message_text: str, exclude_users: List[int] = None
    ) -> Dict[str, int]:
        """Рассылка сообщения пользователям"""
        exclude_users = exclude_users or []
        successful = 0
        failed = 0
        errors = []

        for user_id, user_stat in self.user_stats.items():
            if user_id in exclude_users:
                continue

            try:
                await bot.send_message(user_id, f"📢 {message_text}", parse_mode="HTML")
                successful += 1
                await asyncio.sleep(0.1)  # Задержка чтобы не превысить лимиты

            except Exception as e:
                failed += 1
                errors.append(f"User {user_id}: {str(e)}")
                logger.error(f"Broadcast failed for {user_id}: {e}")

        # Сохраняем историрассылку
        self.broadcast_messages.append(
            {
                "timestamp": datetime.now(),
                "message": message_text,
                "successful": successful,
                "failed": failed,
                "total_users": len(self.user_stats),
            }
        )

        return {
            "successful": successful,
            "failed": failed,
            "total": len(self.user_stats),
            "errors": errors[:10],  # Первые 10 ошибок
        }


# Глобальный экземпляр менеджера админки
admin_manager = AdminManager()
