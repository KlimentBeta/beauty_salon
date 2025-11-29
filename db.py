import mysql.connector
from mysql.connector import Error
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

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
    
    def initialize_table(self, table_name: str, data: list):
        try:
            cursor = self.conn.cursor()

            cursor.execute(f"DELETE FROM `{table_name}`")
            print(f"🧹 Таблица '{table_name}' очищена")

            
            columns = list(data[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join([f"`{col}`" for col in columns])

            sql = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({placeholders})"
            values = [[item[col] for col in columns] for item in data]

            cursor.executemany(sql, values)
            self.conn.commit()

            print(f"✅ В таблицу '{table_name}' добавлено {cursor.rowcount} записей")
            cursor.close()

            return True
        except Error as e:
            print(f"❌ Ошибка запроса к таблице '{table_name}': {e}")
            return False

    def get_service_id(self, service):
        try:
            table_name = 'Service'
            cursor = self.conn.cursor()

            service_clean = service.strip()
    
            sql = f"SELECT ID FROM {table_name} WHERE TRIM(Title) = %s LIMIT 1"
            cursor.execute(sql, (service_clean,))

            result = cursor.fetchone()
            cursor.close()

            if result:
                return result[0] 
            else:
                return None
        except Error as e:
            print(f"❌ Ошибка запроса к таблице '{table_name}': {e}")
            return None
        

    def get_client_id(self, client):
        try:
            table_name = 'Client'
            cursor = self.conn.cursor()

            lastname_clean = client.strip()
    
            sql = f"SELECT ID FROM {table_name} WHERE TRIM(LastName) = %s LIMIT 1"
            cursor.execute(sql, (lastname_clean,))

            result = cursor.fetchone()
            cursor.close()

            if result:
                return result[0] 
            else:
                return None
        except Error as e:
            print(f"❌ Ошибка запроса к таблице '{table_name}': {e}")
            return None
        
    def fetch_all(self, table_name: str):
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM `{table_name}`")
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Ошибка запроса к таблице '{table_name}': {e}")
            return []
        
    def delete_service(self, service_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM Service WHERE id = %s", (service_id,))
            self.conn.commit()  # Обязательно подтверждаем транзакцию
            deleted_rows = cursor.rowcount
            cursor.close()
            return deleted_rows > 0  # True, если хотя бы одна строка удалена
        except Error as e:
            print(f"❌ Ошибка при удалении из таблицы Service: {e}")
            return False

    def fetch_one(self, arg):
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(arg)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            print(f"❌ Ошибка запроса к таблице: {e}")
            return []