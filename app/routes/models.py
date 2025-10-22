from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.services.model_service import ModelService

models_bp = Blueprint('models', __name__)
auth_service = AuthService()
model_service = ModelService()

def get_current_user():
    """Helper function to get current authenticated user"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    return auth_service.get_current_user(auth_header)

@models_bp.route('/test', methods=['POST'])
def test_model():
    """Test a specific model with a message"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        message = data.get('message')
        model_provider = data.get('model_provider', 'openai')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Prepare messages
        messages = [
            {'role': 'user', 'content': message}
        ]
        
        # Generate response
        response = model_service.generate_response(messages, model_provider)
        
        return jsonify({
            'success': response['success'],
            'response': response.get('content'),
            'model_provider': model_provider,
            'metadata': response.get('metadata', {}),
            'error': response.get('error')
        }), 200 if response['success'] else 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@models_bp.route('/available', methods=['GET'])
def get_available_models():
    """Get list of available models"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        models = {
            'openai': {
                'name': 'OpenAI GPT',
                'models': ['gpt-3.5-turbo', 'gpt-4'],
                'description': 'OpenAI\'s GPT models'
            },
            'google': {
                'name': 'Google Gemini',
                'models': ['gemini-pro'],
                'description': 'Google\'s Gemini models'
            }
        }
        
        return jsonify({
            'success': True,
            'models': models
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@models_bp.route('/health', methods=['GET'])
def check_model_health():
    """Check health of all model providers"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        health_status = {}
        
        # Test OpenAI
        try:
            test_messages = [{'role': 'user', 'content': 'Hello'}]
            openai_response = model_service.generate_response_openai(test_messages)
            health_status['openai'] = {
                'status': 'healthy' if openai_response['success'] else 'unhealthy',
                'error': openai_response.get('error')
            }
        except Exception as e:
            health_status['openai'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # Test Google
        try:
            test_messages = [{'role': 'user', 'content': 'Hello'}]
            google_response = model_service.generate_response_google(test_messages)
            health_status['google'] = {
                'status': 'healthy' if google_response['success'] else 'unhealthy',
                'error': google_response.get('error')
            }
        except Exception as e:
            health_status['google'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        return jsonify({
            'success': True,
            'health_status': health_status
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
