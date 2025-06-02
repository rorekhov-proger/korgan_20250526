from flask import Blueprint

# Создаем основной Blueprint
bp = Blueprint('main', __name__)

# Импортируем все маршруты
from app.routes.main_routes import main
from app.routes.auth_routes import auth
from app.routes.chat_routes import chat_bp

# Регистрируем дополнительные blueprints
bp.register_blueprint(chat_bp)

# Определяем, какие модули доступны при импорте из пакета
__all__ = ['bp', 'main', 'auth', 'chat_bp'] 