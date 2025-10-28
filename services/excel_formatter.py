import pandas as pd
from io import BytesIO
# import openpyxl
from openpyxl.styles import Alignment, Border, Side, Font, PatternFill
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.utils import get_column_letter


class ExcelFormatter:
    """Класс для профессионального форматирования Excel"""

    @staticmethod
    def apply_business_formatting(df: pd.DataFrame) -> BytesIO:
        """Применение бизнес-форматирования к отчету"""
        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Аналитика")
            workbook = writer.book
            worksheet = writer.sheets["Аналитика"]

            # Стили форматирования
            thin_border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"),
                top=Side(style="thin"),
                bottom=Side(style="thin"),
            )

            center_alignment = Alignment(horizontal="center", vertical="center")

            # Форматирование заголовков
            for cell in worksheet[1]:
                cell.alignment = center_alignment
                cell.font = Font(bold=True)
                cell.border = thin_border
                cell.fill = PatternFill(
                    start_color="2E86AB", end_color="2E86AB", fill_type="solid"
                )
                cell.font = Font(color="FFFFFF", bold=True)

            # Определение типов колонок
            financial_columns = [
                "Средняя цена розничная",
                "Среднее Вайлдберриз",
                "Выручка",
                "Сумма к перечислению",
                "Сумма услуг доставки",
                "Сумма штрафов",
                "Хранение",
                "Сумма WB Продвижение",
                "Налоги",
                "Себестоимость",
                "Итоговая себестоимость",
                "Чистая прибыль",
            ]

            percent_columns = ["Маржинальность", "Рентабельность"]

            # Форматирование данных
            for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
                for cell in row:
                    cell.alignment = center_alignment
                    cell.border = thin_border

                    # Форматирование финансовых колонок
                    column_name = (
                        df.columns[cell.column - 1]
                        if cell.column <= len(df.columns)
                        else None
                    )
                    if column_name in financial_columns:
                        cell.number_format = '#,##0.00" ₽"'
                    elif column_name in percent_columns:
                        cell.number_format = "0.00%"

            # Условное форматирование
            ExcelFormatter._apply_conditional_formatting(worksheet, df)

            # Автоматическая ширина колонок
            ExcelFormatter._auto_adjust_columns(worksheet)

        output.seek(0)
        return output

    @staticmethod
    def _apply_conditional_formatting(worksheet, df):
        """Применение условного форматирования"""
        if "Маржинальность" in df.columns:
            col_idx = df.columns.get_loc("Маржинальность") + 1
            col_letter = get_column_letter(col_idx)

            rule = ColorScaleRule(
                start_type="num",
                start_value=0,
                start_color="F8696B",
                mid_type="num",
                mid_value=0.1,
                mid_color="FFEB84",
                end_type="num",
                end_value=0.2,
                end_color="63BE7B",
            )
            worksheet.conditional_formatting.add(
                f"{col_letter}2:{col_letter}{worksheet.max_row}", rule
            )

    @staticmethod
    def _auto_adjust_columns(worksheet):
        """Автоматическая настройка ширины колонок"""
        for column in worksheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)

            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass

            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
