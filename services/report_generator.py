import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from config import Config


class ReportGenerator:
    """Генератор различных типов отчетов"""

    @staticmethod
    def generate_comprehensive_pdf(df: pd.DataFrame) -> BytesIO:
        """Генерация комплексного PDF отчета"""
        pdf_buffer = BytesIO()

        with PdfPages(pdf_buffer) as pdf:
            plt.style.use("seaborn-v0_8")

            # 1. Сводная таблица
            ReportGenerator._add_summary_table(pdf, df)

            # 2. Визуализации
            ReportGenerator._add_visualizations(pdf, df)

            # 3. Ключевые метрики
            ReportGenerator._add_key_metrics(pdf, df)

        pdf_buffer.seek(0)
        return pdf_buffer

    @staticmethod
    def _add_summary_table(pdf, df):
        """Добавление сводной таблицы в PDF"""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis("tight")
        ax.axis("off")

        display_df = df.nlargest(15, "Чистая прибыль")[
            [
                "Артикул поставщика",
                "Количество продаж",
                "Чистая прибыль",
                "Маржинальность",
                "Рентабельность",
            ]
        ].copy()

        # Форматирование данных для отображения
        display_df["Чистая прибыль"] = display_df["Чистая прибыль"].apply(
            lambda x: f"{x:,.0f} ₽"
        )
        display_df["Маржинальность"] = (display_df["Маржинальность"] * 100).apply(
            lambda x: f"{x:.1f}%"
        )
        display_df["Рентабельность"] = (display_df["Рентабельность"] * 100).apply(
            lambda x: f"{x:.1f}%"
        )

        table = ax.table(
            cellText=display_df.values,
            colLabels=display_df.columns,
            cellLoc="center",
            loc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.5)
        ax.set_title("ТОП-15 товаров по чистой прибыли", fontsize=16, pad=20)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close()

    @staticmethod
    def _add_visualizations(pdf, df):
        """Добавление визуализаций в PDF"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

        # Круговая диаграмма прибыли
        ReportGenerator._add_profit_pie_chart(ax1, df)

        # Гистограмма маржинальности
        ReportGenerator._add_margin_chart(ax2, df)

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches="tight")
        plt.close()

    @staticmethod
    def _add_profit_pie_chart(ax, df):
        """Добавление круговой диаграммы прибыли"""
        top_n = 5
        top_df = df.nlargest(top_n, "Чистая прибыль")
        other_profit = df["Чистая прибыль"].sum() - top_df["Чистая прибыль"].sum()

        pie_data = pd.concat(
            [
                top_df[["Артикул поставщика", "Чистая прибыль"]],
                pd.DataFrame(
                    [{"Артикул поставщика": "Прочее", "Чистая прибыль": other_profit}]
                ),
            ]
        )

        colors = plt.cm.Set3.colors
        wedges, texts, autotexts = ax.pie(
            pie_data["Чистая прибыль"],
            labels=pie_data["Артикул поставщика"],
            autopct="%1.1f%%",
            startangle=90,
            colors=colors,
        )
        ax.set_title("Распределение прибыли по товарам", fontsize=14)

    @staticmethod
    def _add_margin_chart(ax, df):
        """Добавление гистограммы маржинальности"""
        profitable = df[df["Чистая прибыль"] > 0]
        if not profitable.empty:
            ax.bar(
                profitable["Артикул поставщика"].head(8),
                profitable["Маржинальность"].head(8) * 100,
                color=Config.COLORS["success"],
                alpha=0.7,
            )
            ax.set_title("Маржинальность топ-8 товаров (%)", fontsize=14)
            ax.tick_params(axis="x", rotation=45)
            ax.set_ylabel("Маржинальность, %")

    @staticmethod
    def _add_key_metrics(pdf, df):
        """Добавление ключевых метрик"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axis("off")

        total_metrics = [
            f"Общая выручка: {df['Выручка'].sum():,.0f} ₽",
            f"Общая прибыль: {df['Чистая прибыль'].sum():,.0f} ₽",
            f"Средняя маржинальность: {(df['Маржинальность'].mean() * 100):.1f}%",
            f"Товаров в плюсе: {len(df[df['Чистая прибыль'] > 0])}",
            f"Товаров в минусе: {len(df[df['Чистая прибыль'] < 0])}",
            f"Общее количество продаж: {df['Количество продаж'].sum():,.0f}",
        ]

        ax.text(
            0.1,
            0.9,
            "\n".join(total_metrics),
            fontsize=12,
            verticalalignment="top",
            linespacing=1.5,
        )
        ax.set_title("Ключевые бизнес-метрики", fontsize=16)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close()
