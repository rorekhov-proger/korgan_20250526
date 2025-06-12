from app import db, create_app
from sqlalchemy import inspect
from app.config.config import BaseConfig

app = create_app()

def check_users_table():
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            columns = inspector.get_columns('users')
            print("Структура таблицы 'users':")
            for column in columns:
                print(f"{column['name']} ({column['type']})")
        except Exception as e:
            print(f"Ошибка при проверке таблицы 'users': {e}")
            print(f"Параметры подключения: {BaseConfig.SQLALCHEMY_DATABASE_URI}")

if __name__ == "__main__":
    check_users_table()
