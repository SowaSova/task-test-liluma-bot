import sqlite3
from config import DB_NAME


class DatabaseManager:
    """
    Менеджер для работы с бд пользователей
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        """Внутренний метод для создания таблиц в бд"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                message_id INTEGER,
                company TEXT,
                data_type TEXT
            )
            """)
            conn.commit()

    def create_db(self):
        """Создание дб"""
        self._create_tables()
        print("Database created successfully.")

    def save_message_data(
        self, chat_id: int, message_id: int, company: str, data_type: str
    ):
        """Сохранение данных в бд"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
            INSERT INTO messages (chat_id, message_id, company, data_type)
            VALUES (?, ?, ?, ?)
            """,
                (chat_id, message_id, company, data_type),
            )
            conn.commit()

    def get_message_data(self):
        """Получение данных из бд"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT chat_id, message_id, company, data_type
            FROM messages
            ORDER BY id DESC
            LIMIT 1
            """)
            return cursor.fetchone()

    def update_message_id(
        self, chat_id: int, company: str, data_type: str, new_message_id: int
    ):
        """Обновление данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
            UPDATE messages
            SET message_id = ?
            WHERE chat_id = ? AND company = ? AND data_type = ?
            """,
                (new_message_id, chat_id, company, data_type),
            )
            conn.commit()


if __name__ == "__main__":
    db_manager = DatabaseManager(DB_NAME)
    db_manager.create_db()
