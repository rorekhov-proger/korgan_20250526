import redis
from app.config.config import Config

class RedisService:
    _instance = None
    _redis = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisService, cls).__new__(cls)
        return cls._instance
        
    def __init__(self):
        if RedisService._redis is None:
            RedisService._redis = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                decode_responses=True
            )
            
    @property
    def client(self):
        return RedisService._redis
        
    def set_user_session(self, user_id: str, session_id: str, expire: int = 3600):
        """Сохраняет сессию пользователя"""
        key = f"user_session:{user_id}"
        self.client.set(key, session_id, ex=expire)
        
    def get_user_session(self, user_id: str) -> str:
        """Получает ID сессии пользователя"""
        key = f"user_session:{user_id}"
        return self.client.get(key)
        
    def delete_user_session(self, user_id: str):
        """Удаляет сессию пользователя"""
        key = f"user_session:{user_id}"
        self.client.delete(key)
        
    def set_failed_attempts(self, ip: str, attempts: int = 1, expire: int = 300):
        """Сохраняет количество неудачных попыток входа"""
        key = f"failed_login:{ip}"
        self.client.set(key, attempts, ex=expire)
        
    def get_failed_attempts(self, ip: str) -> int:
        """Получает количество неудачных попыток входа"""
        key = f"failed_login:{ip}"
        attempts = self.client.get(key)
        return int(attempts) if attempts else 0 