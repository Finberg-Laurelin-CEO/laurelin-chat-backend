from datetime import datetime
from typing import Optional, Dict, Any
from google.cloud import firestore

class User:
    """User model for Firestore operations"""
    
    def __init__(self, user_id: str, email: str, name: str = None, 
                 created_at: datetime = None, last_login: datetime = None,
                 preferences: Dict[str, Any] = None):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.created_at = created_at or datetime.utcnow()
        self.last_login = last_login
        self.preferences = preferences or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for Firestore"""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'preferences': self.preferences
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from Firestore document"""
        return cls(
            user_id=data['user_id'],
            email=data['email'],
            name=data.get('name'),
            created_at=data.get('created_at'),
            last_login=data.get('last_login'),
            preferences=data.get('preferences', {})
        )

class UserService:
    """Service class for user operations"""
    
    def __init__(self):
        self.db = firestore.Client()
        self.collection = 'users'
    
    def create_user(self, user: User) -> bool:
        """Create a new user in Firestore"""
        try:
            doc_ref = self.db.collection(self.collection).document(user.user_id)
            doc_ref.set(user.to_dict())
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID from Firestore"""
        try:
            doc_ref = self.db.collection(self.collection).document(user_id)
            doc = doc_ref.get()
            if doc.exists:
                return User.from_dict(doc.to_dict())
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user in Firestore"""
        try:
            doc_ref = self.db.collection(self.collection).document(user_id)
            doc_ref.update(updates)
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user from Firestore"""
        try:
            doc_ref = self.db.collection(self.collection).document(user_id)
            doc_ref.delete()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
