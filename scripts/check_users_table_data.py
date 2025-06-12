from app import db
from app.models.user import User

def check_users_table_data():
    try:
        users = User.query.all()
        print("Содержимое таблицы 'users':")
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Active: {user.is_active}")
    except Exception as e:
        print(f"Ошибка при проверке таблицы 'users': {e}")

if __name__ == "__main__":
    check_users_table_data()
