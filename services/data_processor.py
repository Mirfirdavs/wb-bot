import pandas as pd
from io import BytesIO
from typing import Tuple
from .validators import FileValidator


class DataProcessor:
    """Основной класс для обработки данных"""

    REQUIRED_MAIN_COLUMNS = [
        "Артикул поставщика",
        "Тип документа",
        "Обоснование для оплаты",
        "Цена розничная",
        "Вайлдберриз реализовал Товар (Пр)",
    ]

    REQUIRED_COST_COLUMNS = ["Артикул поставщика", "Себестоимость"]

    @staticmethod
    def read_excel_safe(file_bytes: BytesIO) -> pd.DataFrame:
        """Безопасное чтение Excel файла"""
        try:
            return pd.read_excel(file_bytes, engine="openpyxl")
        except Exception as e:
            raise ValueError(
                "Невозможно прочитать Excel файл. Проверьте формат."
            ) from e

    @staticmethod
    def process_main_report(file_bytes: BytesIO) -> pd.DataFrame:
        """Обработка основного отчета с оптимизацией"""
        df = DataProcessor.read_excel_safe(file_bytes)

        # Валидация колонок
        is_valid, missing_cols = FileValidator.validate_columns(
            df, DataProcessor.REQUIRED_MAIN_COLUMNS
        )
        if not is_valid:
            raise ValueError(f"Отсутствуют обязательные колонки: {missing_cols}")

        # Предварительная обработка
        df = df[df["Артикул поставщика"].notna()]
        df = df.copy()

        # Создаем маски для фильтрации
        sales_mask = df["Тип документа"].str.strip() == "Продажа"
        logistics_mask = df["Обоснование для оплаты"].str.strip() == "Логистика"
        promo_mask = (
            df["Виды логистики, штрафов и корректировок ВВ"].str.strip()
            == "Оказание услуг «WB Продвижение»"
        )

        # Основные агрегации для продаж
        sales_data = (
            df[sales_mask]
            .groupby("Артикул поставщика")
            .agg(
                {
                    "Цена розничная": ["count", "mean", "sum"],
                    "Вайлдберриз реализовал Товар (Пр)": "mean",
                    "К перечислению Продавцу за реализованный Товар": "sum",
                    "Общая сумма штрафов": "sum",
                }
            )
            .round(2)
        )

        # Переименование колонок
        sales_data.columns = [
            "Количество продаж",
            "Средняя цена розничная",
            "Выручка",
            "Среднее Вайлдберриз",
            "Сумма к перечислению",
            "Сумма штрафов",
        ]

        # Дополнительные агрегации
        logistics_data = (
            df[logistics_mask]
            .groupby("Артикул поставщика")["Услуги по доставке товара покупателю"]
            .sum()
            .round(2)
            .rename("Сумма услуг доставки")
        )

        storage_data = (
            df.groupby("Артикул поставщика")["Хранение"]
            .sum()
            .round(2)
            .rename("Хранение")
        )

        promo_data = (
            df[promo_mask]
            .groupby("Артикул поставщика")["Вайлдберриз реализовал Товар (Пр)"]
            .sum()
            .round(2)
            .rename("Сумма WB Продвижение")
        )

        # Объединение всех данных
        result = sales_data.join(
            [logistics_data, storage_data, promo_data], how="left"
        ).fillna(0)

        # Реорганизация колонок
        column_order = [
            "Количество продаж",
            "Средняя цена розничная",
            "Выручка",
            "Среднее Вайлдберриз",
            "Сумма к перечислению",
            "Сумма услуг доставки",
            "Сумма штрафов",
            "Хранение",
            "Сумма WB Продвижение",
        ]

        return result[column_order]

    @staticmethod
    def process_cost_data(
        cost_file_bytes: BytesIO, main_df: pd.DataFrame, tax_rate: float
    ) -> pd.DataFrame:
        """Обработка данных себестоимости"""
        df_cost = DataProcessor.read_excel_safe(cost_file_bytes)

        # Валидация колонок
        is_valid, missing_cols = FileValidator.validate_columns(
            df_cost, DataProcessor.REQUIRED_COST_COLUMNS
        )
        if not is_valid:
            raise ValueError(
                f"В файле себестоимости отсутствуют колонки: {missing_cols}"
            )

        # Объединение данных
        merged = pd.merge(
            main_df,
            df_cost[["Артикул поставщика", "Себестоимость"]],
            on="Артикул поставщика",
            how="left",
        ).fillna(0)

        # Расчет финансовых показателей
        merged["Итоговая себестоимость"] = (
            merged["Себестоимость"] * merged["Количество продаж"]
        ).round(2)

        merged["Налоги"] = (merged["Сумма к перечислению"] * (tax_rate / 100)).round(2)

        # Расчет чистой прибыли
        merged["Чистая прибыль"] = (
            merged["Сумма к перечислению"]
            - merged["Сумма услуг доставки"]
            - merged["Сумма штрафов"]
            - merged["Хранение"]
            - merged["Сумма WB Продвижение"]
            - merged["Налоги"]
            - merged["Итоговая себестоимость"]
        ).round(2)

        # Расчет маржинальности и рентабельности
        merged["Маржинальность"] = (
            merged["Чистая прибыль"] / merged["Выручка"].replace(0, 1)
        ).round(4)

        merged["Рентабельность"] = (
            merged["Чистая прибыль"] / merged["Итоговая себестоимость"].replace(0, 1)
        ).round(4)

        return merged
