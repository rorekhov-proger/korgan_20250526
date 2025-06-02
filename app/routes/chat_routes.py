from flask import Blueprint, jsonify, request
from app import db
from app.models.chat import Chat
from app.models.message import Message
import logging

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/api/chats', methods=['GET'])
def get_chats():
    try:
        chats = Chat.query.order_by(Chat.updated_at.desc()).all()
        return jsonify([chat.to_dict() for chat in chats])
    except Exception as e:
        logging.error(f'Ошибка при получении списка чатов: {str(e)}')
        return jsonify({'error': 'Ошибка при получении списка чатов'}), 500

@chat_bp.route('/api/chats', methods=['POST'])
def create_chat():
    try:
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
    except Exception as e:
        db.session.rollback()
        logging.error(f'Ошибка при создании чата: {str(e)}')
        return jsonify({'error': 'Ошибка при создании чата'}), 500

@chat_bp.route('/api/chats/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    try:
        chat = Chat.query.get_or_404(chat_id)
        db.session.delete(chat)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        logging.error(f'Ошибка при удалении чата {chat_id}: {str(e)}')
        return jsonify({'error': 'Ошибка при удалении чата'}), 500

@chat_bp.route('/api/chats/<int:chat_id>/messages', methods=['GET'])
def get_chat_messages(chat_id):
    try:
        chat = Chat.query.get_or_404(chat_id)
        messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.created_at).all()
        return jsonify([msg.to_dict() for msg in messages])
    except Exception as e:
        logging.error(f'Ошибка при получении сообщений чата {chat_id}: {str(e)}')
        return jsonify({'error': 'Ошибка при получении сообщений'}), 500

@chat_bp.route('/api/chats/<int:chat_id>', methods=['PATCH'])
def update_chat(chat_id):
    try:
        chat = Chat.query.get_or_404(chat_id)
        data = request.get_json()
        
        if not data or 'title' not in data:
            return jsonify({'error': 'Не указано название чата'}), 400
            
        chat.title = data['title']
        db.session.commit()
        
        return jsonify(chat.to_dict())
    except Exception as e:
        db.session.rollback()
        logging.error(f'Ошибка при обновлении чата {chat_id}: {str(e)}')
        return jsonify({'error': 'Ошибка при обновлении чата'}), 500 