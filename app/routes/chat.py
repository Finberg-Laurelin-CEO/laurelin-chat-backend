from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.services.model_service import ModelService
from app.services.ab_testing_service import ABTestingService
from app.models.chat import ChatSession, ChatMessage, MessageRole, ChatService
from app.config import Config
import uuid
from datetime import datetime

chat_bp = Blueprint('chat', __name__)
auth_service = AuthService()
model_service = ModelService()
ab_testing_service = ABTestingService()
chat_service = ChatService()

def get_current_user():
    """Helper function to get current authenticated user"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    return auth_service.get_current_user(auth_header)

@chat_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """Get all chat sessions for current user"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        sessions = chat_service.get_user_sessions(user.user_id)
        return jsonify({
            'success': True,
            'sessions': [session.to_dict() for session in sessions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/sessions', methods=['POST'])
def create_session():
    """Create a new chat session"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        title = data.get('title', f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        session = ChatSession(
            session_id=str(uuid.uuid4()),
            user_id=user.user_id,
            title=title
        )
        
        success = chat_service.create_session(session)
        if not success:
            return jsonify({'error': 'Failed to create session'}), 500
        
        return jsonify({
            'success': True,
            'session': session.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get specific chat session"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        session = chat_service.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        if session.user_id != user.user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'success': True,
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/sessions/<session_id>/messages', methods=['POST'])
def send_message(session_id):
    """Send a message and get AI response"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get session
        session = chat_service.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        if session.user_id != user.user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        user_message = data.get('message')
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Add user message to session
        user_msg = ChatMessage(
            role=MessageRole.USER,
            content=user_message
        )
        session.add_message(user_msg)
        
        # Determine which model to use (A/B testing)
        model_provider = "openai"  # Default
        use_ab_testing = Config.AB_TEST_ENABLED
        
        if use_ab_testing:
            # Use A/B testing via LLM backend
            messages = []
            for msg in session.messages:
                messages.append({
                    'role': msg.role.value,
                    'content': msg.content
                })
            
            # Get AI response via LLM backend with A/B testing
            response = model_service.generate_response_ab_test(
                messages, session_id, user.user_id
            )
        else:
            # Use direct model selection
            if Config.AB_TEST_ENABLED:
                variant = ab_testing_service.assign_user_to_variant(
                    user.user_id, "model_comparison"
                )
                model_provider = variant
            
            # Prepare messages for model
            messages = []
            for msg in session.messages:
                messages.append({
                    'role': msg.role.value,
                    'content': msg.content
                })
            
            # Get AI response
            response = model_service.generate_response(
                messages, model_provider, session_id, user.user_id
            )
        
        if response['success']:
            # Add assistant message to session
            assistant_msg = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=response['content'],
                model_used=model_provider,
                metadata=response.get('metadata', {})
            )
            session.add_message(assistant_msg)
            
            # Track A/B testing event
            if Config.AB_TEST_ENABLED:
                ab_testing_service.track_event(
                    user.user_id,
                    "model_comparison",
                    "message_sent",
                    {
                        'model_provider': model_provider,
                        'session_id': session_id,
                        'response_length': len(response['content'])
                    }
                )
            
            # Update session in database
            chat_service.update_session(session_id, {
                'messages': [msg.to_dict() for msg in session.messages],
                'updated_at': session.updated_at
            })
            
            return jsonify({
                'success': True,
                'response': response['content'],
                'model_used': model_provider,
                'session': session.to_dict()
            }), 200
        else:
            return jsonify({
                'error': 'Failed to generate response',
                'details': response.get('error')
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a chat session"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        session = chat_service.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        if session.user_id != user.user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        success = chat_service.delete_session(session_id)
        if not success:
            return jsonify({'error': 'Failed to delete session'}), 500
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
