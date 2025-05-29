from openai import OpenAI
from app.config.config import Config
import time
from typing import Optional

class GPTService:
    _instance = None
    _client = None
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GPTService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if GPTService._client is None:
            if not Config.OPENAI_API_KEY:
                raise ValueError("OpenAI API ключ не настроен")
            GPTService._client = OpenAI(api_key=Config.OPENAI_API_KEY)

    @property
    def client(self):
        return GPTService._client

    def get_completion(self, user_message: str, retry_count: int = 0) -> Optional[str]:
        if not user_message:
            raise ValueError("Пустое сообщение")

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": (
                        "Ты полезный ассистент, который дает четкие и информативные ответы. "
                        "Ты всегда стараешься помочь пользователю и предоставить релевантную информацию. "
                        "Отвечаешь на русском языке."
                    )},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7,
                presence_penalty=0.6,
                frequency_penalty=0.0
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            if retry_count < self.MAX_RETRIES:
                time.sleep(self.RETRY_DELAY * (retry_count + 1))
                return self.get_completion(user_message, retry_count + 1)
            raise Exception(f"Ошибка GPT после {self.MAX_RETRIES} попыток: {str(e)}") 