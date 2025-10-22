from datetime import datetime
from typing import List, Dict, Any, Optional
from google.cloud import firestore
from enum import Enum

class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage:
    """Individual chat message model"""
    
    def __init__(self, role: MessageRole, content: str, timestamp: datetime = None,
                 model_used: str = None, metadata: Dict[str, Any] = None):
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.utcnow()
        self.model_used = model_used
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for Firestore"""
        return {
            'role': self.role.value,
            'content': self.content,
            'timestamp': self.timestamp,
            'model_used': self.model_used,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Create message from Firestore document"""
        return cls(
            role=MessageRole(data['role']),
            content=data['content'],
            timestamp=data.get('timestamp'),
            model_used=data.get('model_used'),
            metadata=data.get('metadata', {})
        )

class ChatSession:
    """Chat session model"""
    
    def __init__(self, session_id: str, user_id: str, title: str = None,
                 created_at: datetime = None, updated_at: datetime = None,
                 messages: List[ChatMessage] = None, metadata: Dict[str, Any] = None):
        self.session_id = session_id
        self.user_id = user_id
        self.title = title
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.messages = messages or []
        self.metadata = metadata or {}
    
    def add_message(self, message: ChatMessage):
        """Add a message to the session"""
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for Firestore"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'messages': [msg.to_dict() for msg in self.messages],
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """Create session from Firestore document"""
        messages = [ChatMessage.from_dict(msg) for msg in data.get('messages', [])]
        return cls(
            session_id=data['session_id'],
            user_id=data['user_id'],
            title=data.get('title'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            messages=messages,
            metadata=data.get('metadata', {})
        )

class ChatService:
    """Service class for chat operations"""
    
    def __init__(self):
        self.db = firestore.Client()
        self.sessions_collection = 'chat_sessions'
        self.messages_collection = 'chat_messages'
    
    def create_session(self, session: ChatSession) -> bool:
        """Create a new chat session"""
        try:
            doc_ref = self.db.collection(self.sessions_collection).document(session.session_id)
            doc_ref.set(session.to_dict())
            return True
        except Exception as e:
            print(f"Error creating chat session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID"""
        try:
            doc_ref = self.db.collection(self.sessions_collection).document(session_id)
            doc = doc_ref.get()
            if doc.exists:
                return ChatSession.from_dict(doc.to_dict())
            return None
        except Exception as e:
            print(f"Error getting chat session: {e}")
            return None
    
    def get_user_sessions(self, user_id: str, limit: int = 50) -> List[ChatSession]:
        """Get all sessions for a user"""
        try:
            query = (self.db.collection(self.sessions_collection)
                    .where('user_id', '==', user_id)
                    .order_by('updated_at', direction=firestore.Query.DESCENDING)
                    .limit(limit))
            
            sessions = []
            for doc in query.stream():
                sessions.append(ChatSession.from_dict(doc.to_dict()))
            return sessions
        except Exception as e:
            print(f"Error getting user sessions: {e}")
            return []
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update chat session"""
        try:
            doc_ref = self.db.collection(self.sessions_collection).document(session_id)
            doc_ref.update(updates)
            return True
        except Exception as e:
            print(f"Error updating chat session: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete chat session"""
        try:
            doc_ref = self.db.collection(self.sessions_collection).document(session_id)
            doc_ref.delete()
            return True
        except Exception as e:
            print(f"Error deleting chat session: {e}")
            return False
