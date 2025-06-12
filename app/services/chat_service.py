from app import db
from app.models.chat_message import ChatMessage
from app.models.chat import Chat
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        
        logging.info(f"→ Получение истории сообщений для chat_id={chat_id}, page={page}, per_page={per_page}")
        logging.info(f"→ Найдено сообщений: {messages.total}")
            
        return {
            'items': [message.to_dict() for message in messages.items],
            'total': messages.total,
            'pages': messages.pages,
            'current_page': messages.page
        }
    
    @staticmethod
    def save_message(chat_id, role, message_text, chat_title=None):
        """Сохранить новое сообщение в чате"""
        logging.info(f"→ Проверка объекта db: {db}")
        logging.info(f"→ Входящие данные: chat_id={chat_id}, role={role}, message_text={message_text}, chat_title={chat_title}")
        if not db:
            logging.error("[ERROR] Объект db пустой!")
            return None

        chat = Chat.query.get(chat_id)
        if not chat:
            logging.error(f"[ERROR] Чат с ID {chat_id} не найден")
            return None

        try:
            message = ChatMessage(
                chat_id=chat_id,
                role=role,  # Заменено sender_id на role
                message=message_text,
                chat_title=chat_title or "Default Title"  # Установить значение по умолчанию
            )
            db.session.add(message)
            db.session.commit()
            logging.info("→ Сообщение успешно сохранено в базу данных.")
            logging.info(f"→ Сохраненное сообщение: {message.to_dict()}")
            return message.to_dict()
        except Exception as e:
            logging.error(f"[ERROR] Ошибка при сохранении сообщения: {e}", exc_info=True)
            db.session.rollback()
            return None