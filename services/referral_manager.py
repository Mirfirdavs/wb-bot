from typing import Dict, Tuple


class ReferralManager:
    """Менеджер реферальной системы (хранение в оперативной памяти)"""

    def __init__(self):
        # Словарь рефералов: ключ – ID реферала, значение – словарь с referrer (ID пригласившего) и activated (статус активации)
        self.referrals: Dict[int, Dict] = {}
        # Статистика рефереров: ключ – ID пользователя (реферера), значение – словарь с количеством активных и всех рефералов, бонусов
        self.referrer_stats: Dict[int, Dict[str, int]] = {}

    def register_referral(self, referrer_id: int, referral_id: int) -> None:
        """Зарегистрировать нового реферала (связать пригласившего с приглашённым пользователем)."""
        if referrer_id == referral_id or referral_id in self.referrals:
            return

        self.referrals[referral_id] = {"referrer": referrer_id, "activated": False}

        if referrer_id not in self.referrer_stats:
            self.referrer_stats[referrer_id] = {
                "total": 0,  # ➕ добавлено
                "active_count": 0,
                "bonus": 0,
            }

        self.referrer_stats[referrer_id]["total"] += 1  # ➕ учитываем общее число

    def activate_referral(self, referral_id: int) -> bool:
        """Активировать реферала и начислить бонус его рефереру. Возвращает True при успешной активации."""
        info = self.referrals.get(referral_id)
        if not info or info.get("activated"):
            return False

        info["activated"] = True
        referrer_id = info["referrer"]

        if referrer_id not in self.referrer_stats:
            self.referrer_stats[referrer_id] = {
                "total": 1,  # на всякий случай
                "active_count": 0,
                "bonus": 0,
            }

        self.referrer_stats[referrer_id]["active_count"] += 1
        self.referrer_stats[referrer_id]["bonus"] += 1
        return True

    def get_stats(self, user_id: int) -> Tuple[int, int, int]:
        """
        Получить статистику для пользователя: (всего приглашённых, активных рефералов, начислено бонусов).
        """
        stats = self.referrer_stats.get(user_id)
        if not stats:
            return 0, 0, 0
        return (
            stats.get("total", 0),
            stats.get("active_count", 0),
            stats.get("bonus", 0),
        )

    def reset_referrals(self, referrer_id: int) -> None:
        """Сбросить начисленные бонусы для указанного реферера (не затрагивая список рефералов)."""
        if referrer_id in self.referrer_stats:
            self.referrer_stats[referrer_id]["bonus"] = 0


# Единственный экземпляр менеджера рефералов (для использования в других модулях)
referral_manager = ReferralManager()
