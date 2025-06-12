import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.chat import Chat
from app.models.message import Message
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

app = create_app()

engine = create_engine('mysql+mysqlconnector://root:password@localhost/korgan_db')
Session = sessionmaker(bind=engine)
session = Session()

with app.app_context():
    # Удаляем таблицу chats вручную
    session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
    session.execute(text("DROP TABLE IF EXISTS chats;"))
    session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    session.commit()

    print("Таблица chats успешно удалена")

with app.app_context():
    # Удаляем все таблицы
    db.drop_all()
    
    # Создаем все таблицы заново
    db.create_all()
    
    # Удаление всех таблиц
    session.execute("SET FOREIGN_KEY_CHECKS = 0;")
    for table in engine.table_names():
        session.execute(f"DROP TABLE IF EXISTS {table};")
    session.execute("SET FOREIGN_KEY_CHECKS = 1;")
    session.commit()

    # Пересоздание базы данных
    session.execute("CREATE DATABASE IF NOT EXISTS korgan_db;")
    session.commit()
    
    print("База данных успешно пересоздана")