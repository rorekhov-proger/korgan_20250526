from flask import Blueprint, jsonify, request
from app import db
from app.models.chat import Chat
from app.models.chat_message import ChatMessage

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/api/chats', methods=['GET'])
def get_chats():
    chats = Chat.query.order_by(Chat.updated_at.desc()).all()
    return jsonify([chat.to_dict() for chat in chats])

@chat_bp.route('/api/chats', methods=['POST'])
def create_chat():
    data = request.get_json() or {}
    title = data.get('title')
    if not title:
        return jsonify({'error': 'Не указано название чата'}), 400
    chat = Chat(title=title)
    db.session.add(chat)
    db.session.commit()
    welcome_msg = ChatMessage(
        chat_id=chat.id,
        role="assistant",
        message="Привет! Я ваш AI-ассистент. Как я могу помочь вам сегодня?"
    )
    db.session.add(welcome_msg)
    db.session.commit()
    return jsonify(chat.to_dict()), 201

@chat_bp.route('/api/chats/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    db.session.delete(chat)
    db.session.commit()
    return '', 204

@chat_bp.route('/api/chats/<int:chat_id>/messages', methods=['GET'])
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
        print(f"[ERROR] {e}")
        return jsonify({"error": "An error occurred while fetching messages"}), 500

@chat_bp.route('/api/chats/<int:chat_id>', methods=['PATCH'])
def update_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Не указано название чата'}), 400
        
    chat.title = data['title']
    db.session.commit()
    
    return jsonify(chat.to_dict())

@chat_bp.route('/api/chats/<int:chat_id>/messages', methods=['POST'])
def add_message(chat_id):
    data = request.get_json() or {}
    role = data.get('role')
    message = data.get('message')
    if not role or not message:
        return jsonify({'error': 'Role and message are required'}), 400
    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
    chat_message = ChatMessage(chat_id=chat_id, role=role, message=message)
    db.session.add(chat_message)
    db.session.commit()
    return jsonify(chat_message.to_dict()), 201