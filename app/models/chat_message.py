from datetime import datetime
from app import db

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    role = db.Column(db.Enum('user', 'assistant', name='role_enum'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    chat_title = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'role': self.role,
            'message': self.message,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
