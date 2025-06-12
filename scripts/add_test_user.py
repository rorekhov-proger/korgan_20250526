from app import db, create_app
from app.models.user import User

def add_test_user():
    app = create_app()
    with app.app_context():
        try:
            print("→ Проверка объекта db:", db)
            user = User(email="test@example.com", is_active=True)
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            print("Тестовый пользователь успешно добавлен.")
        except Exception as e:
            print(f"Ошибка при добавлении тестового пользователя: {e}")

if __name__ == "__main__":
    add_test_user()
