from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.services.ab_testing_service import ABTestingService

ab_testing_bp = Blueprint('ab_testing', __name__)
auth_service = AuthService()
ab_testing_service = ABTestingService()

def get_current_user():
    """Helper function to get current authenticated user"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    return auth_service.get_current_user(auth_header)

@ab_testing_bp.route('/experiments', methods=['GET'])
def get_experiments():
    """Get all A/B testing experiments"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # This would typically be admin-only, but for demo purposes
        # we'll allow any authenticated user to view experiments
        
        experiments = [
            {
                'name': 'model_comparison',
                'description': 'Compare OpenAI GPT vs Google Gemini performance',
                'status': 'active',
                'variants': {
                    'openai': 0.5,
                    'google': 0.5
                }
            }
        ]
        
        return jsonify({
            'success': True,
            'experiments': experiments
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ab_testing_bp.route('/experiments/<experiment_name>/assign', methods=['POST'])
def assign_to_experiment(experiment_name):
    """Assign user to a specific experiment variant"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        variant = ab_testing_service.assign_user_to_variant(user.user_id, experiment_name)
        
        return jsonify({
            'success': True,
            'experiment_name': experiment_name,
            'variant': variant,
            'user_id': user.user_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ab_testing_bp.route('/experiments/<experiment_name>/track', methods=['POST'])
def track_event(experiment_name):
    """Track an event for A/B testing"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        event_type = data.get('event_type')
        event_data = data.get('event_data', {})
        
        if not event_type:
            return jsonify({'error': 'event_type is required'}), 400
        
        success = ab_testing_service.track_event(
            user.user_id,
            experiment_name,
            event_type,
            event_data
        )
        
        if not success:
            return jsonify({'error': 'Failed to track event'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Event tracked successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ab_testing_bp.route('/experiments/<experiment_name>/results', methods=['GET'])
def get_experiment_results(experiment_name):
    """Get results for a specific experiment"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        results = ab_testing_service.get_experiment_results(experiment_name)
        
        return jsonify({
            'success': True,
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ab_testing_bp.route('/experiments/<experiment_name>/assignment', methods=['GET'])
def get_user_assignment(experiment_name):
    """Get user's assignment for a specific experiment"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        variant = ab_testing_service.assign_user_to_variant(user.user_id, experiment_name)
        
        return jsonify({
            'success': True,
            'experiment_name': experiment_name,
            'variant': variant,
            'user_id': user.user_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
