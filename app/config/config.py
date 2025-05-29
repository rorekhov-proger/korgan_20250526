import os
from dotenv import load_dotenv
from typing import Dict, Any

# Загружаем переменные окружения из .env файла
load_dotenv()

class BaseConfig:
    """Базовая конфигурация"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'm4a'}
    FFMPEG_PATH = r"C:\ffmpeg\bin"

    @classmethod
    def validate_config(cls) -> Dict[str, str]:
        """Проверяет наличие всех необходимых переменных окружения"""
        missing_vars = []
        
        if not cls.OPENAI_API_KEY:
            missing_vars.append("OPENAI_API_KEY")
            
        if not os.path.exists(cls.FFMPEG_PATH):
            missing_vars.append("FFMPEG_PATH (не найден)")
            
        return missing_vars

class DevelopmentConfig(BaseConfig):
    """Конфигурация для разработки"""
    DEBUG = True
    TESTING = False
    
class ProductionConfig(BaseConfig):
    """Конфигурация для продакшена"""
    DEBUG = False
    TESTING = False
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB для продакшена

class TestingConfig(BaseConfig):
    """Конфигурация для тестирования"""
    DEBUG = True
    TESTING = True
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB для тестов

# Выбор конфигурации в зависимости от окружения
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Возвращает нужную конфигурацию на основе переменной окружения"""
    env = os.getenv('FLASK_ENV', 'default')
    return config.get(env, config['default'])

Config = get_config()

def init_app(app):
    """Инициализация приложения"""
    # Проверяем конфигурацию
    missing_vars = Config.validate_config()
    if missing_vars:
        print(f"WARNING: Missing required environment variables: {', '.join(missing_vars)}")
    
    # Создаем папку для загрузок
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    # Добавляем путь к ffmpeg в PATH
    if os.path.exists(Config.FFMPEG_PATH):
        os.environ["PATH"] += os.pathsep + Config.FFMPEG_PATH 