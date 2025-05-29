from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from app.config.config import Config

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Настройка Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'
    
    # Регистрация маршрутов
    from app.routes.main_routes import main
    from app.routes.auth_routes import auth
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    
    # Инициализация конфигурации
    Config.init_app(app)
    
    # Создание таблиц базы данных
    with app.app_context():
        db.create_all()
    
    return app

# Загрузчик пользователя для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id)) 