from datetime import datetime
from typing import Optional, Tuple
import logging
from app.models.user import User
from app.services.redis_service import RedisService
from app import db

class AuthService:
    MAX_LOGIN_ATTEMPTS = 5
    
    def __init__(self):
        self.redis_service = RedisService()
        
    def register_user(self, email: str, username: str, password: str) -> Tuple[bool, str]:
        """Регистрация нового пользователя"""
        try:
            if not email or not username or not password:
                return False, "Все поля обязательны для заполнения"
                
            if User.query.filter_by(email=email).first():
                logging.warning(f"Попытка регистрации с существующим email: {email}")
                return False, "Email уже зарегистрирован"
                
            if User.query.filter_by(username=username).first():
                logging.warning(f"Попытка регистрации с существующим username: {username}")
                return False, "Имя пользователя уже занято"
                
            user = User(email=email, username=username)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            logging.info(f"Успешная регистрация пользователя: {username}")
            return True, "Регистрация успешна"
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Ошибка при регистрации пользователя: {str(e)}")
            return False, f"Ошибка при регистрации: {str(e)}"
            
    def authenticate_user(self, login: str, password: str, ip: str) -> Tuple[bool, str, Optional[User]]:
        """Аутентификация пользователя"""
        try:
            if not login or not password:
                return False, "Логин и пароль обязательны", None
                
            failed_attempts = self.redis_service.get_failed_attempts(ip)
            if failed_attempts >= self.MAX_LOGIN_ATTEMPTS:
                logging.warning(f"Превышено количество попыток входа для IP: {ip}")
                return False, "Слишком много неудачных попыток. Попробуйте позже", None
                
            user = User.query.filter((User.email == login) | (User.username == login)).first()
            
            if not user or not user.check_password(password):
                self.redis_service.set_failed_attempts(ip, failed_attempts + 1)
                logging.warning(f"Неудачная попытка входа для пользователя: {login}, IP: {ip}")
                return False, "Неверный логин или пароль", None
                
            self.redis_service.delete_user_session(ip)
            
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            logging.info(f"Успешный вход пользователя: {user.username}")
            return True, "Вход выполнен успешно", user
            
        except Exception as e:
            logging.error(f"Ошибка при аутентификации: {str(e)}")
            return False, f"Ошибка при аутентификации: {str(e)}", None
            
    def logout_user(self, user_id: str) -> Tuple[bool, str]:
        """Выход пользователя"""
        try:
            if not user_id:
                return False, "Идентификатор пользователя не указан"
                
            self.redis_service.delete_user_session(user_id)
            logging.info(f"Успешный выход пользователя: {user_id}")
            return True, "Выход выполнен успешно"
        except Exception as e:
            logging.error(f"Ошибка при выходе пользователя {user_id}: {str(e)}")
            return False, f"Ошибка при выходе: {str(e)}" 