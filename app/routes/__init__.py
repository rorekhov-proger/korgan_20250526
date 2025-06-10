from flask import Blueprint

bp = Blueprint('main', __name__)

from app.routes.main_routes import main
from app.routes.auth_routes import auth
from app.routes.chat_routes import chat_bp

bp.register_blueprint(chat_bp)

__all__ = ['bp', 'main', 'auth', 'chat_bp']