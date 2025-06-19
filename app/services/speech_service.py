import whisper
import os
import gc
import torch
import logging

class SpeechService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpeechService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if SpeechService._model is None:
            logging.info(f"torch version: {torch.__version__}")
            logging.info(f"torch.cuda.is_available(): {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                logging.info(f"CUDA device count: {torch.cuda.device_count()}")
                logging.info(f"CUDA device name: {torch.cuda.get_device_name(0)}")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logging.info(f"→ Загрузка модели Whisper (device={device})")
            SpeechService._model = whisper.load_model("medium", device=device)
        else:
            logging.info("→ SpeechService временно отключен для тестирования.")

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

            if torch.cuda.is_available():
                logging.info("→ Очистка кеша CUDA")
                torch.cuda.empty_cache()

            logging.info("→ Начало распознавания аудио")
            result = self.model.transcribe(filepath, language="ru")
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
            if torch.cuda.is_available():
                torch.cuda.empty_cache()