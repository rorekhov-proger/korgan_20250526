import whisper
import os
import gc
import torch

class SpeechService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpeechService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if SpeechService._model is None:
            SpeechService._model = whisper.load_model("medium")

    @property
    def model(self):
        return SpeechService._model

    def transcribe_audio(self, filepath):
        try:
            if not os.path.exists(filepath):
                raise ValueError("Файл не существует")

            file_size = os.path.getsize(filepath)
            if file_size < 1000:
                raise ValueError("Файл слишком маленький или пустой")
            
            if file_size > 25 * 1024 * 1024:
                raise ValueError("Файл слишком большой для обработки")

            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            result = self.model.transcribe(filepath, language="ru")
            text = result.get("text", "").strip()

            if not text:
                raise ValueError("Не удалось распознать речь. Возможно, аудио слишком тихое или плохого качества.")

            return text

        except Exception as e:
            raise Exception(f"Ошибка обработки аудио: {str(e)}")

        finally:
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache() 