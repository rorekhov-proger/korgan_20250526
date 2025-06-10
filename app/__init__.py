from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_session import Session
from app.config.config import Config
import os
import logging
from redis import Redis

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Генерируем секретный ключ, если он не установлен
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.urandom(24)
    
    # Настройка сессий
    app.config['SESSION_TYPE'] = 'redis'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 час
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    
    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Настройка Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    login_manager.refresh_view = 'auth.login'
    login_manager.needs_refresh_message = 'Пожалуйста, войдите заново для подтверждения доступа'
    login_manager.needs_refresh_message_category = 'info'
    
    # Настройка Flask-Session
    Session(app)
    
    # Регистрация маршрутов
    from app.routes.main_routes import main
    app.register_blueprint(main)
    
    from app.routes.auth_routes import auth
    app.register_blueprint(auth)
    
    from app.routes.chat_routes import chat_bp
    app.register_blueprint(chat_bp)
    
    # Инициализация конфигурации
    from app import cli
    cli.init_app(app)
    
    # Создание таблиц базы данных
    with app.app_context():
        db.create_all()
    
    # Настройка логирования
    logging.basicConfig(
        filename='app.log',
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s'
    )

    # Проверка подключения к Redis
    try:
        redis_client = Redis(host='localhost', port=6379, decode_responses=True)
        redis_client.ping()
        logging.info("Redis подключен успешно.")
    except Exception as e:
        logging.error(f"Ошибка подключения к Redis: {e}")
        raise RuntimeError("Redis недоступен. Проверьте настройки и запустите сервер Redis.")

    # Глобальная обработка ошибок
    @app.errorhandler(500)
    def internal_server_error(e):
        logging.error(f"Internal Server Error: {e}")
        return render_template('500.html'), 500

    @app.errorhandler(404)
    def not_found_error(e):
        logging.warning(f"Page Not Found: {e}")
        return render_template('404.html'), 404
    
    return app

# Загрузчик пользователя для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    try:
        return User.query.get(int(user_id))
    except:
        return None