from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user with Google token"""
    try:
        data = request.get_json()
        google_token = data.get('token')
        
        if not google_token:
            return jsonify({'error': 'Google token is required'}), 400
        
        result = auth_service.authenticate_user(google_token)
        if not result:
            return jsonify({'error': 'Authentication failed'}), 401

        # Check if user is not authorized (greenlist check failed)
        if 'error' in result and result['error'] == 'not_authorized':
            return jsonify({
                'success': False,
                'error': result['error'],
                'message': result['message']
            }), 403

        return jsonify({
            'success': True,
            'user': result['user'],
            'token': result['token']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    """Verify JWT token"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header is required'}), 400
        
        user = auth_service.get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Invalid token'}), 401
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get current user profile"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header is required'}), 400
        
        user = auth_service.get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Invalid token'}), 401
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header is required'}), 400
        
        user = auth_service.get_current_user(auth_header)
        if not user:
            return jsonify({'error': 'Invalid token'}), 401
        
        data = request.get_json()
        updates = {}
        
        if 'name' in data:
            updates['name'] = data['name']
        if 'preferences' in data:
            updates['preferences'] = data['preferences']
        
        if updates:
            success = auth_service.user_service.update_user(user.user_id, updates)
            if not success:
                return jsonify({'error': 'Failed to update profile'}), 500
        
        # Get updated user
        updated_user = auth_service.user_service.get_user(user.user_id)
        return jsonify({
            'success': True,
            'user': updated_user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
