import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT')
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Firestore Configuration
    FIRESTORE_DATABASE = os.environ.get('FIRESTORE_DATABASE', '(default)')
    
    # Model API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GOOGLE_AI_API_KEY = os.environ.get('GOOGLE_AI_API_KEY')
    
    # A/B Testing Configuration
    AB_TEST_ENABLED = os.environ.get('AB_TEST_ENABLED', 'false').lower() == 'true'
    AB_TEST_SPLIT_RATIO = float(os.environ.get('AB_TEST_SPLIT_RATIO', '0.5'))
    
    # Application Configuration
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    PORT = int(os.environ.get('PORT', 8080))
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:4200').split(',')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
