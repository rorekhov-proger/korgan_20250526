from flask import Blueprint

bp = Blueprint('main', __name__)

from app.routes.main_routes import main
from app.routes.auth_routes import auth

__all__ = ['main', 'auth'] 