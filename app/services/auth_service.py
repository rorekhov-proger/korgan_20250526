from datetime import datetime
from typing import Optional, Tuple
from app.models.user import User
from app.services.redis_service import RedisService
from app import db

class AuthService:
    def __init__(self):
        self.redis_service = RedisService()
        
    def register_user(self, email: str, username: str, password: str) -> Tuple[bool, str]:
        """Регистрация нового пользователя"""
        try:
            if User.query.filter_by(email=email).first():
                return False, "Email уже зарегистрирован"
                
            if User.query.filter_by(username=username).first():
                return False, "Имя пользователя уже занято"
                
            user = User(email=email, username=username)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return True, "Регистрация успешна"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Ошибка при регистрации: {str(e)}"
            
    def authenticate_user(self, login: str, password: str, ip: str) -> Tuple[bool, str, Optional[User]]:
        """Аутентификация пользователя"""
        try:
            # Проверяем количество неудачных попыток
            failed_attempts = self.redis_service.get_failed_attempts(ip)
            if failed_attempts >= 5:
                return False, "Слишком много неудачных попыток. Попробуйте позже", None
                
            # Ищем пользователя по email или username
            user = User.query.filter((User.email == login) | (User.username == login)).first()
            
            if not user or not user.check_password(password):
                # Увеличиваем счетчик неудачных попыток
                self.redis_service.set_failed_attempts(ip, failed_attempts + 1)
                return False, "Неверный логин или пароль", None
                
            # Сбрасываем счетчик неудачных попыток
            self.redis_service.delete_user_session(ip)
            
            # Обновляем время последнего входа
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            return True, "Вход выполнен успешно", user
            
        except Exception as e:
            return False, f"Ошибка при аутентификации: {str(e)}", None
            
    def logout_user(self, user_id: str):
        """Выход пользователя"""
        try:
            self.redis_service.delete_user_session(user_id)
            return True, "Выход выполнен успешно"
        except Exception as e:
            return False, f"Ошибка при выходе: {str(e)}" 