import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, create_app
from app.models.chat_message import ChatMessage

# Создаем контекст приложения Flask
app = create_app()
with app.app_context():
    def check_chat_messages():
        try:
            messages = ChatMessage.query.all()
            print("Содержимое таблицы 'chat_messages':")
            for message in messages:
                print(message.to_dict())
        except Exception as e:
            print(f"Ошибка при проверке таблицы 'chat_messages': {e}")

    check_chat_messages()
    # Проверка таблицы chat_message
    messages = ChatMessage.query.all()
    if messages:
        print("→ Найденные сообщения в таблице chat_message:")
        for message in messages:
            print(message.to_dict())
    else:
        print("→ Таблица chat_message пуста.")
