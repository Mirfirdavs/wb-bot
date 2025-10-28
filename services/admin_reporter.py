import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import List
from .admin_manager import admin_manager, UserStat


class AdminReporter:
    """Генератор отчетов для админки"""

    @staticmethod
    def generate_users_excel() -> BytesIO:
        """Генерация Excel с пользователями"""
        df = admin_manager.get_user_stats_df()

        if df.empty:
            raise ValueError("Нет данных о пользователях")

        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Основной лист
            df.to_excel(writer, sheet_name="Пользователи", index=False)

            # Лист с общей статистикой
            stats = admin_manager.get_bot_stats()
            stats_df = pd.DataFrame(
                [
                    {"Метрика": "Всего пользователей", "Значение": stats.total_users},
                    {"Метрика": "Активных за сегодня", "Значение": stats.active_today},
                    {
                        "Метрика": "Всего файлов обработано",
                        "Значение": stats.total_files,
                    },
                    {"Метрика": "Аптайм (дни)", "Значение": f"{stats.uptime_days:.1f}"},
                    {
                        "Метрика": "Использование памяти (MB)",
                        "Значение": f"{stats.memory_usage_mb:.1f}",
                    },
                ]
            )

            stats_df.to_excel(writer, sheet_name="Статистика", index=False)

            # Лист с топ пользователями
            top_users = admin_manager.get_top_users(20)
            top_data = []
            for user in top_users:
                top_data.append(
                    {
                        "ID": user.user_id,
                        "Username": f"@{user.username}" if user.username else "Нет",
                        "Имя": user.first_name or "Нет",
                        "Сессий": user.sessions_count,
                        "Файлов": user.files_processed,
                        "Последняя активность": user.last_activity.strftime(
                            "%Y-%m-%d %H:%M"
                        )
                        if user.last_activity
                        else "Нет",
                    }
                )

            top_df = pd.DataFrame(top_data)
            top_df.to_excel(writer, sheet_name="Топ пользователи", index=False)

        output.seek(0)
        return output

    @staticmethod
    def generate_activity_chart() -> BytesIO:
        """Генерация графика активности"""
        df = admin_manager.get_user_stats_df()

        if df.empty:
            raise ValueError("Нет данных для графика")

        # Группировка по дням
        df["last_activity"] = pd.to_datetime(df["last_activity"])
        daily_activity = df.groupby(df["last_activity"].dt.date).size()

        plt.figure(figsize=(12, 6))

        # График активности
        plt.subplot(1, 2, 1)
        daily_activity.tail(14).plot(kind="bar", color="skyblue")  # Последние 14 дней
        plt.title("Активность по дням (14 дней)")
        plt.xlabel("Дата")
        plt.ylabel("Активных пользователей")
        plt.xticks(rotation=45)

        # Круговая диаграмма по файлам
        plt.subplot(1, 2, 2)
        file_stats = df["files_processed"].value_counts().head(5)
        plt.pie(file_stats.values, labels=file_stats.index, autopct="%1.1f%%")
        plt.title("Распределение по файлам")

        plt.tight_layout()

        output = BytesIO()
        plt.savefig(output, format="png", dpi=150, bbox_inches="tight")
        plt.close()

        output.seek(0)
        return output

    @staticmethod
    def format_stats_message() -> str:
        """Форматирование сообщения со статистикой"""
        stats = admin_manager.get_bot_stats()
        df = admin_manager.get_user_stats_df()

        if not df.empty:
            avg_files_per_user = df["files_processed"].mean()
            most_active = df.loc[df["files_processed"].idxmax()]
        else:
            avg_files_per_user = 0
            most_active = None

        message = [
            "🤖 <b>СТАТИСТИКА БОТА</b>",
            "",
            f"👥 <b>Пользователи:</b> {stats.total_users}",
            f"📈 <b>Активных сегодня:</b> {stats.active_today}",
            f"📁 <b>Обработано файлов:</b> {stats.total_files}",
            f"📊 <b>Файлов на пользователя:</b> {avg_files_per_user:.1f}",
            f"⏰ <b>Аптайм:</b> {stats.uptime_days:.1f} дней",
            f"💾 <b>Память:</b> {stats.memory_usage_mb:.1f} MB",
            "",
        ]

        if most_active is not None and not pd.isna(most_active["user_id"]):
            username = (
                most_active["username"]
                if most_active["username"] != "Нет"
                else "без username"
            )
            message.extend(
                [
                    "🏆 <b>Самый активный пользователь:</b>",
                    f"ID: {most_active['user_id']}",
                    f"Username: {username}",
                    f"Файлов: {most_active['files_processed']}",
                    f"Сессий: {most_active['sessions']}",
                ]
            )

        return "\n".join(message)
