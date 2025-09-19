"""GPT service with compatibility for modern (openai>=1.x) and legacy (openai<1) SDKs.
Also supports local Ollama when model starts with 'ollama:'.
"""
from app.config.config import Config
import time
from typing import Optional, List, Dict
import logging
import requests
from requests.exceptions import RequestException
import os

# Try modern SDK first, fallback to legacy
try:
    from openai import OpenAI as OpenAIClient  # type: ignore
    _MODERN_OPENAI = True
    _legacy_openai = None
except Exception:  # ImportError or others
    OpenAIClient = None
    _MODERN_OPENAI = False
    try:
        import openai as _legacy_openai  # type: ignore
    except Exception:
        _legacy_openai = None

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

            # Simple connectivity test (works for both modern and legacy endpoints)
            try:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }
                logging.info("[GPTService] Выполняется тестовый запрос /models...")
                test_response = requests.get(
                    f"{base_url}/models",
                    headers=headers,
                    timeout=10,
                )
                if test_response.status_code == 200:
                    logging.info("[GPTService] Тестовый запрос прошёл успешно.")
                else:
                    logging.warning(
                        f"[GPTService] Тест API вернул код {test_response.status_code}: {test_response.text[:200]}"
                    )
            except RequestException as e:
                logging.warning(f"[GPTService] Ошибка тестового запроса: {str(e)}")

            # Initialize client (modern preferred, legacy fallback)
            if _MODERN_OPENAI and OpenAIClient is not None:
                GPTService._client = OpenAIClient(api_key=api_key, base_url=base_url)
                logging.info("[GPTService] Используется современный OpenAI SDK (chat.completions)")
            elif _legacy_openai is not None:
                # Legacy SDK configuration
                try:
                    _legacy_openai.api_key = api_key
                    # Different legacy versions: api_base vs base_url
                    if hasattr(_legacy_openai, "api_base"):
                        _legacy_openai.api_base = base_url
                    else:
                        setattr(_legacy_openai, "api_base", base_url)
                except Exception:
                    pass
                GPTService._client = _legacy_openai
                logging.info("[GPTService] Используется legacy OpenAI SDK (ChatCompletion)")
            else:
                raise ImportError(
                    "Не найден совместимый OpenAI SDK. Установите пакет 'openai' версии 1.x или 0.28.x"
                )

    @property
    def client(self):
        return GPTService._client

    def get_completion(self, messages, model: str = "gpt-5-nano", retry_count: int = 0) -> Optional[str]:
        # messages — список словарей [{"role": ..., "content": ...}]
        if not messages or not isinstance(messages, list):
            raise ValueError("Пустой список сообщений для GPT")
        try:
            logging.info(
                f"[GPTService] Отправка истории в API. Попытка {retry_count + 1}/{self.MAX_RETRIES + 1}"
            )
            # Route to Ollama if requested (model value like 'ollama:llama3.1')
            if isinstance(model, str) and model.lower().startswith('ollama:'):
                ollama_model = model.split(':', 1)[1].strip() or 'llama3.1'
                # Resolve common aliases to concrete tags to avoid 404
                def _resolve_alias(name: str) -> str:
                    base = name.lower().strip()
                    if base == 'llama3.1':
                        return 'llama3.1:8b'
                    if base == 'qwen2.5':
                        return 'qwen2.5:7b-instruct'
                    return name
                ollama_model = _resolve_alias(ollama_model)
                return self._ollama_chat(messages, ollama_model)
            # Modern SDK
            if _MODERN_OPENAI and OpenAIClient is not None and hasattr(self.client, "chat"):
                response = self.client.chat.completions.create(model=model, messages=messages)
                logging.info(f"[GPTService] Ответ от API (modern): {str(response)[:200]}")
                return response.choices[0].message.content.strip()
            # Legacy SDK
            elif hasattr(self.client, "ChatCompletion"):
                response = self.client.ChatCompletion.create(model=model, messages=messages)
                logging.info(f"[GPTService] Ответ от API (legacy): {str(response)[:200]}")
                return response["choices"][0]["message"]["content"].strip()
            else:
                raise RuntimeError("Неподдерживаемый клиент OpenAI SDK")
        except Exception as e:
            logging.error(f"[GPTService] Ошибка при запросе: {str(e)}")
            if retry_count < self.MAX_RETRIES:
                wait = self.RETRY_DELAY * (retry_count + 1)
                logging.info(f"[GPTService] Повтор запроса через {wait} секунд...")
                time.sleep(wait)
                return self.get_completion(messages, model, retry_count + 1)
            raise Exception(f"[GPTService] Ошибка после {self.MAX_RETRIES} попыток: {str(e)}")

    def _ollama_chat(self, messages: List[Dict[str, str]], model: str) -> str:
        base_url = (os.getenv('OLLAMA_BASE_URL') or 'http://localhost:11434').rstrip('/')
        url = f"{base_url}/api/chat"
        # Сообщения совместимы: {role: 'user'|'assistant'|'system', content: '...'}
        payload = {
            'model': model,
            'messages': messages,
            'stream': False,
            'options': { 'temperature': 0 }
        }
        logging.info(f"[GPTService] Ollama chat → model={model} url={url}")
        try:
            resp = requests.post(url, json=payload, timeout=60)
        except RequestException as e:
            raise RuntimeError(f"Ошибка запроса к Ollama: {e}")
        if resp.status_code != 200:
            raise RuntimeError(f"Ollama вернул {resp.status_code}: {resp.text[:300]}")
        data = resp.json()
        # Формат /api/chat (stream=false) содержит message.content
        msg = (data.get('message') or {})
        content = (msg.get('content') or '').strip()
        if not content:
            # Некоторые сборки могут возвращать 'response'
            content = (data.get('response') or '').strip()
        if not content:
            raise RuntimeError("Пустой ответ от Ollama")
        return content