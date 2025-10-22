import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from google.auth.transport import requests
from google.oauth2 import id_token
from app.models.user import User, UserService

class AuthService:
    """Authentication service for handling user auth"""
    
    def __init__(self):
        self.user_service = UserService()
        self.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
        self.google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    
    def verify_google_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Google ID token and return user info"""
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                self.google_client_id
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return {
                'user_id': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo.get('name'),
                'picture': idinfo.get('picture')
            }
        except ValueError as e:
            print(f"Token verification failed: {e}")
            return None
    
    def create_jwt_token(self, user_id: str) -> str:
        """Create JWT token for authenticated user"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError:
            print("Invalid token")
            return None
    
    def authenticate_user(self, google_token: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with Google token and return user info with JWT"""
        # Verify Google token
        google_user_info = self.verify_google_token(google_token)
        if not google_user_info:
            return None
        
        # Get or create user
        user = self.user_service.get_user(google_user_info['user_id'])
        if not user:
            # Create new user
            user = User(
                user_id=google_user_info['user_id'],
                email=google_user_info['email'],
                name=google_user_info.get('name')
            )
            self.user_service.create_user(user)
        else:
            # Update last login
            self.user_service.update_user(user.user_id, {
                'last_login': datetime.utcnow()
            })
        
        # Create JWT token
        jwt_token = self.create_jwt_token(user.user_id)
        
        return {
            'user': user.to_dict(),
            'token': jwt_token
        }
    
    def get_current_user(self, auth_header: str) -> Optional[User]:
        """Get current user from Authorization header"""
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        user_id = self.verify_jwt_token(token)
        if not user_id:
            return None
        
        return self.user_service.get_user(user_id)
