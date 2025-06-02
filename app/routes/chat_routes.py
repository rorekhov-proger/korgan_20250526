from flask import Blueprint, jsonify, request
from app import db
from app.models.chat import Chat
from app.models.message import Message

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/api/chats', methods=['GET'])
def get_chats():
    chats = Chat.query.order_by(Chat.updated_at.desc()).all()
    return jsonify([chat.to_dict() for chat in chats])

@chat_bp.route('/api/chats', methods=['POST'])
def create_chat():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Не указано название чата'}), 400
        
    chat = Chat(title=data['title'])
    db.session.add(chat)
    db.session.commit()
    
    welcome_msg = Message(
        content="Привет! Я ваш AI-ассистент. Как я могу помочь вам сегодня?",
        role="assistant",
        chat_id=chat.id
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
    chat = Chat.query.get_or_404(chat_id)
    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at).all()
    return jsonify([msg.to_dict() for msg in messages])

@chat_bp.route('/api/chats/<int:chat_id>', methods=['PATCH'])
def update_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Не указано название чата'}), 400
        
    chat.title = data['title']
    db.session.commit()
    
    return jsonify(chat.to_dict()) 