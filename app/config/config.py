import os
from dotenv import load_dotenv
from typing import Dict, Any

# Загружаем переменные окружения из .env файла
print("Загрузка .env файла...")
load_dotenv()

class BaseConfig:
    """Базовая конфигурация"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_API_BASE_URL = os.getenv('OPENAI_API_BASE_URL', 'https://api.openai.com/v1')
    OPENAI_PROJECT_ID = os.getenv('OPENAI_PROJECT_ID', 'proj_q9HWIMPFxlHs4MBuauU0aYie')
    
    # Отладочный вывод
    print(f"[Config] OPENAI_API_KEY: {OPENAI_API_KEY[:10]}... (скрыт)")
    print(f"[Config] OPENAI_API_BASE_URL: {OPENAI_API_BASE_URL}")
    print(f"[Config] OPENAI_PROJECT_ID: {OPENAI_PROJECT_ID}")
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'm4a'}
    FFMPEG_PATH = r"C:\ffmpeg\bin"

    # MySQL конфигурация
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'korgan_db')
    
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis конфигурация
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    @classmethod
    def validate_config(cls) -> Dict[str, str]:
        """Проверяет наличие всех необходимых переменных окружения"""
        missing_vars = []
        
        if not cls.OPENAI_API_KEY:
            missing_vars.append("OPENAI_API_KEY")
            
        if not os.path.exists(cls.FFMPEG_PATH):
            missing_vars.append("FFMPEG_PATH (не найден)")
            
        if not cls.MYSQL_PASSWORD:
            missing_vars.append("MYSQL_PASSWORD")
            
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
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # Используем SQLite в памяти для тестов

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