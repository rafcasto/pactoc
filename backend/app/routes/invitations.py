from flask import Blueprint, request, jsonify
from ..middleware.auth import require_auth
from ..services.invitation_service import InvitationService
from ..models.patient_invitation import PatientInvitation
from ..utils.responses import success_response, error_response

invitations_bp = Blueprint('invitations', __name__, url_prefix='/api/invitations')

@invitations_bp.route('/', methods=['POST'])
@require_auth
def create_invitation():
    """Create a new patient invitation."""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('email'):
            return error_response('Email is required', 400)
        
        email = data['email']
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        
        # Get current user from auth middleware
        user_uid = request.user.get('uid')
        
        # Create invitation
        invitation, public_link = InvitationService.create_invitation(
            email, user_uid, first_name, last_name
        )
        
        if not invitation:
            return error_response(public_link, 500)  # public_link contains error message
        
        return success_response({
            'invitation': invitation,
            'public_link': public_link
        }, 'Invitation created successfully')
        
    except Exception as e:
        return error_response(f'Error creating invitation: {str(e)}', 500)

@invitations_bp.route('/', methods=['GET'])
@require_auth
def list_invitations():
    """Get all invitations created by the current user."""
    try:
        user_uid = request.user.get('uid')
        
        # Get query parameters
        status = request.args.get('status')  # pending, completed, expired
        
        invitations = PatientInvitation.get_all_by_user(user_uid)
        
        # Filter by status if provided
        if status:
            invitations = [inv for inv in invitations if inv['status'] == status]
        
        # Add public links to pending invitations
        for invitation in invitations:
            if invitation['status'] == 'pending':
                invitation['public_link'] = InvitationService._generate_public_link(invitation['token'])
        
        return success_response({
            'invitations': invitations,
            'total': len(invitations)
        })
        
    except Exception as e:
        return error_response(f'Error retrieving invitations: {str(e)}', 500)

@invitations_bp.route('/<invitation_id>', methods=['GET'])
@require_auth
def get_invitation(invitation_id):
    """Get a specific invitation."""
    try:
        invitation = PatientInvitation.get_by_id(invitation_id)
        
        if not invitation:
            return error_response('Invitation not found', 404)
        
        # Check if user owns this invitation
        user_uid = request.user.get('uid')
        if invitation['invited_by_uid'] != user_uid:
            return error_response('Access denied', 403)
        
        # Add public link if pending
        if invitation['status'] == 'pending':
            invitation['public_link'] = InvitationService._generate_public_link(invitation['token'])
        
        return success_response({'invitation': invitation})
        
    except Exception as e:
        return error_response(f'Error retrieving invitation: {str(e)}', 500)

@invitations_bp.route('/<invitation_id>/resend', methods=['PUT'])
@require_auth
def resend_invitation(invitation_id):
    """Resend invitation email."""
    try:
        # Check if invitation exists and user owns it
        invitation = PatientInvitation.get_by_id(invitation_id)
        if not invitation:
            return error_response('Invitation not found', 404)
        
        user_uid = request.user.get('uid')
        if invitation['invited_by_uid'] != user_uid:
            return error_response('Access denied', 403)
        
        # Resend invitation
        success, error_msg = InvitationService.resend_invitation(invitation_id)
        
        if not success:
            return error_response(error_msg, 400)
        
        # Get updated invitation
        updated_invitation = PatientInvitation.get_by_id(invitation_id)
        updated_invitation['public_link'] = InvitationService._generate_public_link(updated_invitation['token'])
        
        return success_response({
            'invitation': updated_invitation
        }, 'Invitation resent successfully')
        
    except Exception as e:
        return error_response(f'Error resending invitation: {str(e)}', 500)

@invitations_bp.route('/<invitation_id>', methods=['DELETE'])
@require_auth
def cancel_invitation(invitation_id):
    """Cancel (expire) an invitation."""
    try:
        # Check if invitation exists and user owns it
        invitation = PatientInvitation.get_by_id(invitation_id)
        if not invitation:
            return error_response('Invitation not found', 404)
        
        user_uid = request.user.get('uid')
        if invitation['invited_by_uid'] != user_uid:
            return error_response('Access denied', 403)
        
        # Cancel invitation
        success = PatientInvitation.cancel_invitation(invitation_id)
        
        if not success:
            return error_response('Error canceling invitation', 500)
        
        return success_response(message='Invitation canceled successfully')
        
    except Exception as e:
        return error_response(f'Error canceling invitation: {str(e)}', 500)

@invitations_bp.route('/stats', methods=['GET'])
@require_auth
def get_invitation_stats():
    """Get invitation statistics for the current user."""
    try:
        user_uid = request.user.get('uid')
        
        invitations = PatientInvitation.get_all_by_user(user_uid)
        
        stats = {
            'total': len(invitations),
            'pending': len([inv for inv in invitations if inv['status'] == 'pending']),
            'completed': len([inv for inv in invitations if inv['status'] == 'completed']),
            'expired': len([inv for inv in invitations if inv['status'] == 'expired'])
        }
        
        return success_response({'stats': stats})
        
    except Exception as e:
        return error_response(f'Error retrieving stats: {str(e)}', 500)
