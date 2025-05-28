#pip install -r requirements.txt
from flask import Flask, request, jsonify, send_from_directory
import whisper
import os
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

app = Flask(__name__, static_folder='', template_folder='')

model = whisper.load_model("medium")

@app.route("/")
def index():
    return send_from_directory('', 'index.html')

@app.route("/login")
def login():
    return "Страница входа"

@app.route("/logout")
def logout():
    return "Вы вышли из системы"

@app.route("/home")
def home():
    return "Добро пожаловать домой!"

@app.route("/upload", methods=["POST"])
def upload():
    if "audio_file" not in request.files:
        return jsonify({"error": "Файл не найден"}), 400

    audio = request.files["audio_file"]
    upload_folder = "temp"
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, audio.filename)
    audio.save(filepath)
    print(f"Файл сохранён: {filepath}")

    try:
        if os.path.getsize(filepath) < 1000:
            os.remove(filepath)
            return jsonify({"text": "Файл слишком мал или пуст. Проверьте файл."})

        result = model.transcribe(filepath, language="ru")
        text = result.get("text", "").strip()

        if not text:
            text = "Не удалось распознать речь. Возможно, аудио слишком тихое или плохого качества."

        os.remove(filepath)
        print("Файл удалён")

        return jsonify({"text": text})

    except Exception as e:
        print(f"Ошибка на сервере: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        error_message = str(e)
        if "ffmpeg" in error_message.lower():
            return jsonify({"text": "Ошибка обработки аудио. Возможно, формат файла не поддерживается."})
        elif "decode" in error_message.lower() or "not found" in error_message.lower():
            return jsonify({"text": "Не удалось прочитать аудио. Проверьте формат и целостность файла."})
        else:
            return jsonify({"text": f"Произошла ошибка при обработке: {error_message}"}), 500
if __name__ == "__main__":
    app.run(debug=True)