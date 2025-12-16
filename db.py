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
        
    def delete_service(self, service_id: int):
        try:
            # Попытка удалить напрямую — если есть FK, будет исключение
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM Service WHERE ID = %s", (service_id,))
            self.conn.commit()
            cursor.close()
            return True, "Услуга успешно удалена."

        except Error as e:
            self.conn.rollback()  # откатываем, если что-то пошло не так
            err_msg = str(e)

            # Обработка известных ошибок
            if "1451" in err_msg or "foreign key constraint fails" in err_msg:
                return False, "Невозможно удалить: услуга уже назначена клиентам."
            elif "1062" in err_msg:  # дубликат — не актуально для DELETE, но для примера
                return False, "Ошибка: нарушение уникальности."
            else:
                return False, f"Ошибка БД: {err_msg[:100]}..."  # обрезаем длинные сообщения

        except Exception as e:
            self.conn.rollback()
            return False, f"Внутренняя ошибка: {str(e)}"

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

    def execute(self, query, params=None):  # ← params=None делает аргумент необязательным
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(query, params or ())  # ← если params=None → подставляем пустой кортеж
            if cursor.rowcount >= 0:
                self.conn.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Ошибка запроса к таблице: {e}")
            self.conn.rollback()
            return False

    def add_service(self, Title: str, Cost: float, DurationInSeconds: int,
                Description: str = None, Discount: float = None, MainImagePath: str = None) -> bool:
     """
     Добавляет новую услугу в таблицу Service.
     Возвращает ID новой записи при успехе, иначе False (но по вашему стилю — лучше bool).
     Однако, судя по предпочтению — возвращаем bool, как в delete_service.
     """
     try:
         cursor = self.conn.cursor()
    
         # Проверка на длину Title и MainImagePath (на всякий, т.к. БД может не проверить клиентски)
         if len(Title) > 100:
             print("❌ Title превышает 100 символов")
             return False
         if MainImagePath and len(MainImagePath) > 1000:
             print("❌ MainImagePath превышает 1000 символов")
             return False
    
         query = """
             INSERT INTO Service (Title, Cost, DurationInSeconds, Description, Discount, MainImagePath)
             VALUES (%s, %s, %s, %s, %s, %s)
         """
         cursor.execute(query, (
             Title,
             Cost,
             DurationInSeconds,
             Description,
             Discount,        # Передаём как есть: если 0.15 = 15%, то вызывающий код должен сам делить
             MainImagePath
         ))
    
         self.conn.commit()
         inserted_id = cursor.lastrowid  # ID новой записи
         cursor.close()
    
         # Вы можете вернуть inserted_id (int), но по вашему стилю — bool:
         # return inserted_id is not None
         return True
    
     except Exception as e:
         print(f"❌ Ошибка при добавлении услуги в таблицу Service: {e}")
         # Откатываем транзакцию при ошибке (если autocommit=False)
         try:
             self.conn.rollback()
         except:
             pass
         return False