from app import create_app, db
from app.models.chat import Chat
from app.models.message import Message

app = create_app()

with app.app_context():
    # Удаляем все таблицы
    db.drop_all()
    
    # Создаем все таблицы заново
    db.create_all()
    
    print("База данных успешно пересоздана") 