from flask import Blueprint, request, jsonify
from ..utils.auth_utils import require_auth, get_current_user_uid
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
        user_uid = get_current_user_uid()
        
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
        user_uid = get_current_user_uid()
        
        # Get query parameters
        status = request.args.get('status')  # pending, completed, expired
        
        # Get nutritionist first
        from ..models.sql_models import Nutritionist
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Get invitations for this nutritionist
        query = PatientInvitation.query.filter_by(nutritionist_id=nutritionist.id)
        
        # Filter by status if provided
        if status:
            query = query.filter_by(status=status)
        
        invitations = [inv.to_dict() for inv in query.all()]
        
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
        user_uid = get_current_user_uid()
        
        # Get nutritionist first
        from ..models.sql_models import Nutritionist
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Get invitation and verify ownership
        invitation = PatientInvitation.query.filter_by(
            id=invitation_id,
            nutritionist_id=nutritionist.id
        ).first()
        
        if not invitation:
            return error_response('Invitation not found', 404)
        
        invitation_dict = invitation.to_dict()
        
        # Add public link if pending
        if invitation.status == 'pending':
            invitation_dict['public_link'] = InvitationService._generate_public_link(invitation.token)
        
        return success_response({'invitation': invitation_dict})
        
    except Exception as e:
        return error_response(f'Error retrieving invitation: {str(e)}', 500)

@invitations_bp.route('/<invitation_id>/resend', methods=['PUT'])
@require_auth
def resend_invitation(invitation_id):
    """Resend invitation email."""
    try:
        user_uid = get_current_user_uid()
        
        # Get nutritionist first
        from ..models.sql_models import Nutritionist
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Check if invitation exists and user owns it
        invitation = PatientInvitation.query.filter_by(
            id=invitation_id,
            nutritionist_id=nutritionist.id
        ).first()
        
        if not invitation:
            return error_response('Invitation not found', 404)
        
        # Resend invitation
        success, error_msg = InvitationService.resend_invitation(invitation_id)
        
        if not success:
            return error_response(error_msg, 400)
        
        # Get updated invitation
        updated_invitation = PatientInvitation.query.get(invitation_id)
        invitation_dict = updated_invitation.to_dict()
        invitation_dict['public_link'] = InvitationService._generate_public_link(updated_invitation.token)
        
        return success_response({
            'invitation': invitation_dict
        }, 'Invitation resent successfully')
        
    except Exception as e:
        return error_response(f'Error resending invitation: {str(e)}', 500)

@invitations_bp.route('/<invitation_id>', methods=['DELETE'])
@require_auth
def cancel_invitation(invitation_id):
    """Cancel (expire) an invitation."""
    try:
        user_uid = get_current_user_uid()
        
        # Get nutritionist first
        from ..models.sql_models import Nutritionist
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Check if invitation exists and user owns it
        invitation = PatientInvitation.query.filter_by(
            id=invitation_id,
            nutritionist_id=nutritionist.id
        ).first()
        
        if not invitation:
            return error_response('Invitation not found', 404)
        
        # Cancel invitation
        invitation.status = 'expired'
        from ..services.database_service import db
        db.session.commit()
        
        return success_response(message='Invitation canceled successfully')
        
    except Exception as e:
        return error_response(f'Error canceling invitation: {str(e)}', 500)

@invitations_bp.route('/stats', methods=['GET'])
@require_auth
def get_invitation_stats():
    """Get invitation statistics for the current user."""
    try:
        user_uid = get_current_user_uid()
        
        # Get nutritionist first
        from ..models.sql_models import Nutritionist
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        invitations = PatientInvitation.query.filter_by(nutritionist_id=nutritionist.id).all()
        invitations = [inv.to_dict() for inv in invitations]
        
        stats = {
            'total': len(invitations),
            'pending': len([inv for inv in invitations if inv['status'] == 'pending']),
            'completed': len([inv for inv in invitations if inv['status'] == 'completed']),
            'expired': len([inv for inv in invitations if inv['status'] == 'expired'])
        }
        
        return success_response({'stats': stats})
        
    except Exception as e:
        return error_response(f'Error retrieving stats: {str(e)}', 500)
