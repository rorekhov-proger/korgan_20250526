from flask import Blueprint, request, jsonify, send_from_directory, render_template, redirect, url_for
from flask_login import login_required, current_user
import os
from app.services.speech_service import SpeechService
from app.services.gpt_service import GPTService
from app.config.config import Config

main = Blueprint('main', __name__)
speech_service = SpeechService()
gpt_service = GPTService()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@main.route("/")
def root():
    if current_user.is_authenticated:
        return redirect(url_for('main.chat'))
    return redirect(url_for('auth.login'))

@main.route("/chat")
@login_required
def chat():
    return render_template('index.html')

@main.route("/upload", methods=["POST"])
@login_required
def upload():
    if "audio_file" not in request.files:
        return jsonify({"error": "Файл не найден"}), 400

    audio = request.files["audio_file"]
    
    if not audio.filename:
        return jsonify({"error": "Пустое имя файла"}), 400
        
    if not allowed_file(audio.filename):
        return jsonify({"error": f"Недопустимый формат файла. Разрешены: {', '.join(Config.ALLOWED_EXTENSIONS)}"}), 400
    
    if request.content_length > Config.MAX_CONTENT_LENGTH:
        return jsonify({"error": f"Файл слишком большой. Максимальный размер: {Config.MAX_CONTENT_LENGTH // (1024*1024)}MB"}), 413

    filepath = os.path.join(Config.UPLOAD_FOLDER, audio.filename)
    
    try:
        audio.save(filepath)
        text = speech_service.transcribe_audio(filepath)
        if not text:
            return jsonify({"error": "Не удалось распознать речь в аудио"}), 400
        return jsonify({"text": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass

@main.route("/gpt", methods=["POST"])
@login_required
def gpt():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Отсутствуют данные запроса"}), 400
            
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Пустое сообщение"}), 400

        model = data.get("model", "gpt-3.5-turbo")  # Get model from request or use default
        reply = gpt_service.get_completion(user_message, model=model)
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500 