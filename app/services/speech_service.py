import whisper
import os

class SpeechService:
    def __init__(self):
        self.model = whisper.load_model("medium")

    def transcribe_audio(self, filepath):
        try:
            if os.path.getsize(filepath) < 1000:
                raise ValueError("File is too small or empty")

            result = self.model.transcribe(filepath, language="ru")
            text = result.get("text", "").strip()

            if not text:
                raise ValueError("Could not recognize speech. Audio might be too quiet or of poor quality.")

            return text

        except Exception as e:
            raise Exception(f"Error processing audio: {str(e)}") 