import os
import gc
import logging
from app.config.config import Config
from typing import Optional

ASR_BACKEND = os.getenv('ASR_BACKEND', 'whisper').lower()

class SpeechService:
    _instance = None
    _model: Optional[object] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpeechService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Инициализация отложена до первого вызова (ленивая)
        pass

    @property
    def model(self):
        return SpeechService._model

    def transcribe_audio(self, filepath):
        try:
            logging.info(f"→ Проверка существования файла: {filepath}")
            if not os.path.exists(filepath):
                raise ValueError("Файл не существует")

            file_size = os.path.getsize(filepath)
            logging.info(f"→ Размер файла: {file_size} байт")
            if file_size < 1000:
                raise ValueError("Файл слишком маленький или пустой")
            
            if file_size > 25 * 1024 * 1024:
                raise ValueError("Файл слишком большой для обработки")

            # backend: Ollama (с автоматическим фолбэком на Whisper при ошибке/404)
            if ASR_BACKEND == 'ollama':
                try:
                    from app.services.ollama_service import OllamaASR
                    logging.info("→ Используется Ollama ASR backend")
                    client = OllamaASR()
                    if not client.model_exists():
                        raise RuntimeError(f"Модель Ollama '{client.model}' не установлена. Фолбэк на Whisper.")
                    text = client.transcribe(filepath)
                    logging.info(f"→ Распознанный текст (Ollama): {text}")
                    return text
                except Exception as ollama_err:
                    msg = str(ollama_err)
                    logging.warning(f"→ Ollama ASR не сработал: {msg}. Пытаемся Whisper…")
                    # продолжаем к Whisper ниже

            # backend: Whisper (по умолчанию)
            try:
                import torch  # type: ignore
            except Exception:
                torch = None
            if torch is not None and getattr(torch, 'cuda', None) and torch.cuda.is_available():
                logging.info("→ Очистка кеша CUDA")
                torch.cuda.empty_cache()

            # Ленивая загрузка Whisper
            if SpeechService._model is None:
                try:
                    import whisper  # type: ignore
                except Exception as e:
                    raise RuntimeError("Библиотека openai-whisper не установлена. Установите её или переключите ASR_BACKEND=ollama")
                device = "cpu"
                if torch is not None and getattr(torch, 'cuda', None) and torch.cuda.is_available():
                    device = "cuda"
                logging.info(f"→ Загрузка модели Whisper (device={device})")
                SpeechService._model = whisper.load_model("medium", device=device)

            logging.info("→ Начало распознавания аудио")
            result = SpeechService._model.transcribe(filepath, language="ru")
            text = result.get("text", "").strip()

            if not text:
                raise ValueError("Не удалось распознать речь. Возможно, аудио слишком тихое или плохого качества.")

            logging.info(f"→ Распознанный текст: {text}")
            return text

        except Exception as e:
            logging.error(f"→ Ошибка обработки аудио: {str(e)}")
            raise Exception(f"Ошибка обработки аудио: {str(e)}")

        finally:
            gc.collect()
            try:
                import torch  # type: ignore
                if getattr(torch, 'cuda', None) and torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except Exception:
                pass