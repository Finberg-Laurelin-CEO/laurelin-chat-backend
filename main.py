import os
from app import create_app
from app.config import config

# Create Flask app
app = create_app(config.get(os.environ.get('FLASK_ENV', 'development')))

@app.route("/")
def index():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "laurelin-chat-backend",
        "version": "1.0.0"
    }

@app.route("/health")
def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "laurelin-chat-backend",
        "version": "1.0.0",
        "environment": os.environ.get('FLASK_ENV', 'development')
    }

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))