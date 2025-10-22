import os
from flask import Flask
from flask_cors import CORS
from app.config import Config

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS for frontend integration
    CORS(app, origins=[
        "http://localhost:4200",  # Angular dev server
        "https://your-frontend-domain.com"  # Production frontend
    ])
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp
    from app.routes.models import models_bp
    from app.routes.ab_testing import ab_testing_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(models_bp, url_prefix='/api/models')
    app.register_blueprint(ab_testing_bp, url_prefix='/api/ab-testing')
    
    return app
