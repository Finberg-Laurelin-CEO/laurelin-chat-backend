from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.models.greenlist import GreenlistService

greenlist_bp = Blueprint('greenlist', __name__)
auth_service = AuthService()
greenlist_service = GreenlistService()

def require_admin():
    """Decorator to require admin access (checks if user is authenticated)"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'Authorization header is required'}), 401

    user = auth_service.get_current_user(auth_header)
    if not user:
        return jsonify({'error': 'Invalid token'}), 401

    # TODO: Add proper admin role check when role system is implemented
    # For now, just check if user is authenticated
    return None

@greenlist_bp.route('/check', methods=['POST'])
def check_email():
    """Check if an email is on the greenlist"""
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        is_allowed = greenlist_service.is_email_allowed(email)

        return jsonify({
            'success': True,
            'email': email,
            'is_allowed': is_allowed
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@greenlist_bp.route('/list', methods=['GET'])
def list_greenlist():
    """List all greenlist entries (requires admin)"""
    try:
        # Check admin access
        error_response = require_admin()
        if error_response:
            return error_response

        active_only = request.args.get('active_only', 'true').lower() == 'true'
        entries = greenlist_service.list_all(active_only=active_only)

        return jsonify({
            'success': True,
            'count': len(entries),
            'entries': [entry.to_dict() for entry in entries]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@greenlist_bp.route('/add', methods=['POST'])
def add_to_greenlist():
    """Add email to greenlist (requires admin)"""
    try:
        # Check admin access
        error_response = require_admin()
        if error_response:
            return error_response

        data = request.get_json()
        email = data.get('email')
        notes = data.get('notes')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Get current user for audit trail
        auth_header = request.headers.get('Authorization')
        current_user = auth_service.get_current_user(auth_header)

        success = greenlist_service.add_email(
            email=email,
            added_by=current_user.email if current_user else None,
            notes=notes
        )

        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully added {email} to greenlist'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to add email to greenlist'
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@greenlist_bp.route('/bulk-add', methods=['POST'])
def bulk_add_to_greenlist():
    """Bulk add emails to greenlist (requires admin)"""
    try:
        # Check admin access
        error_response = require_admin()
        if error_response:
            return error_response

        data = request.get_json()
        emails = data.get('emails', [])

        if not emails or not isinstance(emails, list):
            return jsonify({'error': 'Emails array is required'}), 400

        # Get current user for audit trail
        auth_header = request.headers.get('Authorization')
        current_user = auth_service.get_current_user(auth_header)

        results = greenlist_service.bulk_add_emails(
            emails=emails,
            added_by=current_user.email if current_user else None
        )

        return jsonify({
            'success': True,
            'results': results
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@greenlist_bp.route('/remove', methods=['POST'])
def remove_from_greenlist():
    """Remove email from greenlist (soft delete, requires admin)"""
    try:
        # Check admin access
        error_response = require_admin()
        if error_response:
            return error_response

        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        success = greenlist_service.remove_email(email)

        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully removed {email} from greenlist'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to remove email from greenlist'
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@greenlist_bp.route('/delete', methods=['DELETE'])
def delete_from_greenlist():
    """Permanently delete email from greenlist (requires admin)"""
    try:
        # Check admin access
        error_response = require_admin()
        if error_response:
            return error_response

        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        success = greenlist_service.delete_email(email)

        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully deleted {email} from greenlist'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete email from greenlist'
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@greenlist_bp.route('/get/<email>', methods=['GET'])
def get_greenlist_entry(email):
    """Get greenlist entry details (requires admin)"""
    try:
        # Check admin access
        error_response = require_admin()
        if error_response:
            return error_response

        entry = greenlist_service.get_entry(email)

        if entry:
            return jsonify({
                'success': True,
                'entry': entry.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Email not found in greenlist'
            }), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500
