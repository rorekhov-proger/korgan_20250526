from datetime import datetime
from app import db

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Message {self.id} in Chat {self.chat_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'role': self.role,
            'chat_id': self.chat_id,
            'created_at': self.created_at.isoformat()
        } 