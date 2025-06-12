from app import db

def test_mysql_connection():
    try:
        connection = db.engine.connect()
        print("Успешное подключение к MySQL!")
        connection.close()
    except Exception as e:
        print(f"Ошибка подключения к MySQL: {e}")

if __name__ == "__main__":
    test_mysql_connection()
