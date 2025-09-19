import os
import base64
import requests
from typing import Optional


class OllamaASR:
    def __init__(self,
                 base_url: Optional[str] = None,
                 model: Optional[str] = None,
                 timeout: int = 120):
        self.base_url = (base_url or os.getenv('OLLAMA_BASE_URL') or 'http://localhost:11434').rstrip('/')
        self.model = model or os.getenv('OLLAMA_ASR_MODEL') or 'whisper'
        self.timeout = timeout

    def transcribe(self, filepath: str) -> str:
        if not os.path.exists(filepath):
            raise ValueError('Файл не существует')
        with open(filepath, 'rb') as f:
            audio_b64 = base64.b64encode(f.read()).decode('utf-8')

        # Используем /api/generate (поддерживается whisper в Ollama)
        url = f"{self.base_url}/api/generate"
        payload = {
            'model': self.model,
            'prompt': 'Transcribe the following audio to plain text (language: Russian if detected).',
            'audio': audio_b64,
            'stream': False,
            'options': { 'temperature': 0 }
        }
        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
        except requests.RequestException as e:
            raise RuntimeError(f"Ошибка подключения к Ollama: {e}")

        if resp.status_code != 200:
            detail = resp.text
            if resp.status_code == 404:
                raise RuntimeError(
                    f"Ollama вернул 404 для модели '{self.model}'. Модель не найдена. "
                    f"Проверьте тег и установите доступную аудио-модель или переключитесь на Whisper. Ответ: {detail}"
                )
            raise RuntimeError(f"Ollama вернул код {resp.status_code}: {detail}")

        data = resp.json()
        # По спецификации Ollama /api/generate возвращает поле "response" при stream=false
        text = (data.get('response') or '').strip()
        if not text:
            raise RuntimeError('Ollama не вернул текст распознавания')
        return text

    def model_exists(self) -> bool:
        try:
            url = f"{self.base_url}/api/tags"
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                return False
            data = resp.json() or {}
            models = data.get('models') or []
            names = {m.get('name') for m in models if isinstance(m, dict)}
            return self.model in names
        except Exception:
            return False
