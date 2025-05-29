from flask import Blueprint, request, jsonify, send_from_directory, render_template
import os
from app.services.speech_service import SpeechService
from app.services.gpt_service import GPTService
from app.config.config import Config

main = Blueprint('main', __name__)
speech_service = SpeechService()
gpt_service = GPTService()

@main.route("/")
def index():
    return render_template('index.html')

@main.route("/upload", methods=["POST"])
def upload():
    if "audio_file" not in request.files:
        return jsonify({"error": "File not found"}), 400

    audio = request.files["audio_file"]
    filepath = os.path.join(Config.UPLOAD_FOLDER, audio.filename)
    
    try:
        audio.save(filepath)
        text = speech_service.transcribe_audio(filepath)
        return jsonify({"text": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@main.route("/gpt", methods=["POST"])
def gpt():
    data = request.get_json()
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    try:
        reply = gpt_service.get_completion(user_message)
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500 