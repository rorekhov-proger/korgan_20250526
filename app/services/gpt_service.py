from openai import OpenAI
from app.config.config import Config
import time
from typing import Optional
import logging
import requests
from requests.exceptions import RequestException

class GPTService:
    _instance = None
    _client = None
    MAX_RETRIES = 3
    RETRY_DELAY = 1

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GPTService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if GPTService._client is None:
            api_key = Config.OPENAI_API_KEY
            base_url = Config.OPENAI_API_BASE_URL

            if not api_key:
                raise ValueError("OpenAI API ключ не настроен")

            logging.info(f"[GPTService] Используется API ключ: {api_key[:10]}... (скрыт)")
            logging.info(f"[GPTService] Используется базовый URL: {base_url}")

            try:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                logging.info("[GPTService] Выполняется тестовый запрос /models...")
                test_response = requests.get(
                    f"{base_url}/models",
                    headers=headers,
                    timeout=10
                )
                if test_response.status_code == 200:
                    logging.info("[GPTService] Тестовый запрос прошёл успешно.")
                    models = test_response.json()
                    logging.info(f"[GPTService] Доступные модели: {models}")
                else:
                    logging.error(f"[GPTService] Ошибка теста API. Код: {test_response.status_code}")
                    logging.error(f"[GPTService] Ответ: {test_response.text}")
            except RequestException as e:
                logging.error(f"[GPTService] Ошибка при тестовом запросе: {str(e)}")

            GPTService._client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )

    @property
    def client(self):
        return GPTService._client

    def get_completion(self, user_message: str, model: str = "gpt-3.5-turbo", retry_count: int = 0) -> Optional[str]:
        if not user_message:
            raise ValueError("Пустое сообщение")

        try:
            logging.info(f"[GPTService] Отправка сообщения в API. Попытка {retry_count + 1}/{self.MAX_RETRIES + 1}")
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": user_message}]
            )
            logging.info(f"[GPTService] Ответ от API: {response}")
            return response.choices[0].message.content.strip()

        except Exception as e:
            logging.error(f"[GPTService] Ошибка при запросе: {str(e)}")

            if retry_count < self.MAX_RETRIES:
                wait = self.RETRY_DELAY * (retry_count + 1)
                logging.info(f"[GPTService] Повтор запроса через {wait} секунд...")
                time.sleep(wait)
                return self.get_completion(user_message, model, retry_count + 1)

            raise Exception(f"[GPTService] Ошибка после {self.MAX_RETRIES} попыток: {str(e)}")