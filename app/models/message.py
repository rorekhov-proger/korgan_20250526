from app import db

class Chat(db.Model):
    __tablename__ = 'chat'

    id = db.Column(db.Integer, primary_key=True)
    # other fields...

    def __repr__(self):
        return f'<Chat {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            # other fields...
        }