import mysql.connector
from mysql.connector import Error

# ── Константы подключения ───────────────────────
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "beauty_salon"
DB_USER = "kali"
DB_PASSWORD = "Kali@2025!"


def get_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            autocommit=True
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return None
    
class Database():
    def __init__(self):
        self.conn = get_connection()

    
    def fetch_all(self, table_name: str):
        if not self.conn or not self.conn.is_connected():
            print("⚠️ Нет подключения к БД")
            return []

        if not table_name.replace('_', '').isalnum():
            raise ValueError(f"Недопустимое имя таблицы: {table_name}")

        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM `{table_name}`")
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Ошибка запроса к таблице '{table_name}': {e}")
            return []