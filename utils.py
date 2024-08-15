from typing import Optional
from io import BytesIO
from matplotlib import pyplot as plt


def generate_chart_buffer(
    company: str, data_type: str, data: Optional[float] = None
) -> BytesIO:
    """Генерация графика и возвращение его в буфере"""
    fig, ax = plt.subplots(figsize=(6, 4))
    if data is not None:
        ax.bar([data_type], [data])
    else:
        ax.bar([data_type], [0])
    ax.set_title(f"{data_type.capitalize()} компании {company}")

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    return buffer


def initialize_table(tm):
    """Создание таблицы и заполнение начальными данными"""
    if not tm.table_exists():
        tm.create_table_with_data()


def initialize_database(dbm):
    """Создание бд sqlite для хранения данных"""
    dbm._create_tables()
