from app import db
from app.models.chat_message import ChatMessage

class ChatService:
    @staticmethod
    def get_chat_history(chat_id, page=1, per_page=50):
        """Получить историю сообщений для конкретного чата с пагинацией
        
        Args:
            chat_id (int): ID чата
            page (int): Номер страницы (начиная с 1)
            per_page (int): Количество сообщений на странице
        """
        messages = ChatMessage.query.filter_by(chat_id=chat_id)\
            .order_by(ChatMessage.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        print(f"→ Получение истории сообщений для chat_id={chat_id}, page={page}, per_page={per_page}")
        print(f"→ Найдено сообщений: {messages.total}")
            
        return {
            'items': [message.to_dict() for message in messages.items],
            'total': messages.total,
            'pages': messages.pages,
            'current_page': messages.page
        }
    
    @staticmethod
    def save_message(chat_id, sender_id, message_text):
        """Сохранить новое сообщение в чате"""
        message = ChatMessage(
            chat_id=chat_id,
            sender_id=sender_id,
            message=message_text
        )
        db.session.add(message)
        db.session.commit()
        return message.to_dict()