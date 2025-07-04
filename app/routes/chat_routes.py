from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app import db
from app.models.chat import Chat
from app.models.chat_message import ChatMessage
from app.services.protocol_service import generate_protocol_markdown, save_markdown
from app.services.protocol_extract import extract_protocol_data
from app.utils.api_error_handler import api_error_handler
import logging

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/api/chats', methods=['GET'])
@login_required
@api_error_handler
def get_chats():
    chats = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.updated_at.desc()).all()
    return jsonify([chat.to_dict() for chat in chats])

@chat_bp.route('/api/chats', methods=['POST'])
@login_required
@api_error_handler
def create_chat():
    data = request.get_json() or {}
    title = data.get('title')
    if not title:
        logging.error('Не указано название чата')
        return jsonify({'error': 'Не указано название чата'}), 400
    try:
        chat = Chat(title=title, user_id=current_user.id)
        db.session.add(chat)
        db.session.commit()
        try:
            chat = Chat.query.get(chat.id)
            if not chat:
                raise ValueError(f"Чат с ID {chat.id} не найден после фиксации транзакции")
            welcome_msg = ChatMessage(
                chat_id=chat.id,
                chat_title=chat.title,
                role="assistant",
                message="Привет! Я ваш AI-ассистент. Как я могу помочь вам сегодня?"
            )
            db.session.add(welcome_msg)
            db.session.commit()
        except Exception as e:
            logging.error(f"Ошибка при добавлении приветственного сообщения: {str(e)}")
            return jsonify({'error': 'Ошибка сервера при добавлении сообщения'}), 500
        return jsonify(chat.to_dict()), 201
    except Exception as e:
        logging.error(f"Ошибка при создании чата: {str(e)}")
        return jsonify({'error': 'Ошибка сервера'}), 500

@chat_bp.route('/api/chat/<int:chat_id>', methods=['DELETE'])
@api_error_handler
def delete_chat(chat_id):
    try:
        ChatMessage.query.filter_by(chat_id=chat_id).delete()
        db.session.commit()
        chat = Chat.query.get_or_404(chat_id)
        db.session.delete(chat)
        db.session.commit()
        return '', 204
    except Exception as e:
        logging.error(f"Ошибка при удалении чата: {e}")
        return jsonify({'error': 'Не удалось удалить чат'}), 500

@chat_bp.route('/api/chat/<int:chat_id>/messages', methods=['GET'])
@api_error_handler
def get_chat_messages(chat_id):
    """Получение сообщений для конкретного чата"""
    try:
        chat = Chat.query.get(chat_id)
        if not chat:
            return jsonify({"error": "Chat not found"}), 404
        messages = ChatMessage.query.filter_by(chat_id=chat_id).order_by(ChatMessage.created_at).all()
        return jsonify([{
            "id": message.id,
            "role": message.role,
            "message": message.message,
            "created_at": message.created_at.isoformat()
        } for message in messages])
    except Exception as e:
        logging.error(f"[ERROR] {e}")
        return jsonify({"error": "An error occurred while fetching messages"}), 500

@chat_bp.route('/api/chats/<int:chat_id>', methods=['PATCH'])
@api_error_handler
def update_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Не указано название чата'}), 400
    chat.title = data['title']
    db.session.commit()
    return jsonify(chat.to_dict())

@chat_bp.route('/api/chat/<int:chat_id>/messages', methods=['POST'])
@api_error_handler
def send_message(chat_id):
    """Обработать отправку сообщения в чат"""
    data = request.get_json() or {}
    role = data.get('role')
    message_text = data.get('message')
    if not role or not message_text:
        logging.error('Не указаны role или текст сообщения')
        return jsonify({'error': 'Не указаны role или текст сообщения'}), 400
    try:
        chat = Chat.query.get(chat_id)
        if not chat:
            logging.error(f"Чат с ID {chat_id} не найден")
            return jsonify({'error': 'Чат не найден'}), 404
        from app.services.chat_service import ChatService
        saved_message = ChatService.save_message(chat_id, role, message_text, chat_title=chat.title)
        if not saved_message:
            raise ValueError("Ошибка при сохранении сообщения")
        return jsonify(saved_message), 201
    except Exception as e:
        logging.error(f"Ошибка при обработке сообщения: {str(e)}")
        return jsonify({'error': 'Ошибка сервера'}), 500

@chat_bp.route('/api/protocol/generate', methods=['POST'])
@api_error_handler
def generate_protocol():
    """
    Принимает JSON с распознанным текстом и параметром mode ('full' или 'fast'),
    извлекает данные, формирует Markdown и возвращает ссылку на скачивание.
    """
    data = request.get_json() or {}
    mode = data.get('mode', 'full')  # 'full' или 'fast'
    protocol_data = data.get('protocol_data')
    if not protocol_data:
        return jsonify({'error': 'Нет данных для протокола'}), 400
    # Генерация Markdown
    md_content = generate_protocol_markdown(protocol_data, mode=mode)
    md_link = save_markdown(md_content)
    return jsonify({'download_url': md_link})

@chat_bp.route('/api/protocol/extract', methods=['POST'])
@api_error_handler
def extract_and_generate_protocol():
    """
    Принимает текст (или результат распознавания речи) и mode ('full'/'fast'),
    извлекает данные, формирует Markdown и возвращает ссылку на скачивание.
    """
    data = request.get_json() or {}
    text = data.get('text', '')
    mode = data.get('mode', 'full')
    if not text:
        return jsonify({'error': 'Нет текста для обработки'}), 400
    protocol_data = extract_protocol_data(text, mode=mode)
    md_content = generate_protocol_markdown(protocol_data, mode=mode)
    md_link = save_markdown(md_content)
    return jsonify({'download_url': md_link})

@chat_bp.route('/api/protocol/extract_json', methods=['POST'])
@api_error_handler
def extract_protocol_json():
    """
    Принимает текст и mode, возвращает JSON-структуру протокола для редактирования.
    """
    data = request.get_json() or {}
    text = data.get('text', '')
    mode = data.get('mode', 'full')
    if not text:
        return jsonify({'error': 'Нет текста для обработки'}), 400
    protocol_data = extract_protocol_data(text, mode=mode)
    return jsonify({'protocol_data': protocol_data})