from models.user import db
from datetime import datetime
from cryptography.fernet import Fernet
import os

class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    token = db.Column(db.Text, nullable=False)  # Encrypted token
    username = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    knowledge_bases = db.relationship('KnowledgeBase', backref='bot', lazy=True, cascade='all, delete-orphan')
    conversations = db.relationship('Conversation', backref='bot', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Bot {self.name}>'
    
    def encrypt_token(self, token):
        """Encrypt the bot token for secure storage"""
        key = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
        f = Fernet(key)
        self.token = f.encrypt(token.encode()).decode()
    
    def decrypt_token(self):
        """Decrypt the bot token for use"""
        key = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
        f = Fernet(key)
        return f.decrypt(self.token.encode()).decode()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'knowledge_bases_count': len(self.knowledge_bases)
        }


class KnowledgeBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    bot_id = db.Column(db.Integer, db.ForeignKey('bot.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('Document', backref='knowledge_base', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<KnowledgeBase {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'bot_id': self.bot_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'documents_count': len(self.documents)
        }


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    knowledge_base_id = db.Column(db.Integer, db.ForeignKey('knowledge_base.id'), nullable=False)
    processed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    chunks = db.relationship('TextChunk', backref='document', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Document {self.filename}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'knowledge_base_id': self.knowledge_base_id,
            'processed': self.processed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'chunks_count': len(self.chunks)
        }


class TextChunk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    chunk_index = db.Column(db.Integer, nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TextChunk {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content[:200] + '...' if len(self.content) > 200 else self.content,
            'chunk_index': self.chunk_index,
            'document_id': self.document_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_user_id = db.Column(db.String(50), nullable=False)
    telegram_username = db.Column(db.String(100))
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    bot_id = db.Column(db.Integer, db.ForeignKey('bot.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Conversation {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'telegram_user_id': self.telegram_user_id,
            'telegram_username': self.telegram_username,
            'message': self.message,
            'response': self.response,
            'bot_id': self.bot_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

