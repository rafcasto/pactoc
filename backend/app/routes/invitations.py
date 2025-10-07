from flask import Blueprint, request, jsonify
from ..utils.auth_utils import require_auth, get_current_user_uid
from ..services.invitation_service import InvitationService
from ..models.patient_invitation import PatientInvitation
from ..services.database_service import db
from ..utils.responses import success_response, error_response
from datetime import datetime

invitations_bp = Blueprint('invitations', __name__, url_prefix='/api/invitations')

@invitations_bp.route('/register-nutritionist', methods=['POST'])
@require_auth
def register_nutritionist():
    """Register the current user as a nutritionist."""
    try:
        user_uid = get_current_user_uid()
        
        if not user_uid:
            return error_response('Invalid authentication - no user UID found', 401)
        
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('email'):
            return error_response('Email is required', 400)
        if not data.get('first_name'):
            return error_response('First name is required', 400)
        if not data.get('last_name'):
            return error_response('Last name is required', 400)
        
        # Check if nutritionist already exists
        from ..models.sql_models import Nutritionist
        existing = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if existing:
            return success_response({
                'nutritionist': existing.to_dict(),
                'message': 'Nutritionist already registered'
            })
        
        # Check if email already exists
        existing_email = Nutritionist.query.filter_by(email=data['email']).first()
        if existing_email:
            return error_response('Email already registered to another nutritionist', 400)
        
        # Create new nutritionist
        nutritionist = Nutritionist(
            firebase_uid=user_uid,
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone=data.get('phone'),
            license_number=data.get('license_number'),
            specialization=data.get('specialization'),
            bio=data.get('bio'),
            is_active=True,
            is_verified=True,  # Auto-verify for now
            verification_date=datetime.utcnow()
        )
        
        db.session.add(nutritionist)
        db.session.commit()
        
        return success_response({
            'nutritionist': nutritionist.to_dict()
        }, 'Nutritionist registered successfully', 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error registering nutritionist: {str(e)}', 500)

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
        
        if not user_uid:
            return error_response('Invalid authentication - no user UID found', 401)
        
        # Get query parameters
        status = request.args.get('status')  # pending, completed, expired
        
        # Get nutritionist first
        from ..models.sql_models import Nutritionist
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            # Auto-register the user as a nutritionist with basic info
            # In a production system, you'd want a proper registration flow
            try:
                # Extract email from Firebase token if available
                user_email = getattr(request, 'user', {}).get('email', f'user-{user_uid[:8]}@example.com')
                
                nutritionist = Nutritionist(
                    firebase_uid=user_uid,
                    email=user_email,
                    first_name='Nutritionist',
                    last_name=user_uid[:8],  # Use part of UID as temp last name
                    is_active=True,
                    is_verified=True,
                    verification_date=datetime.utcnow()
                )
                
                db.session.add(nutritionist)
                db.session.commit()
                
                print(f"Auto-registered new nutritionist: {user_uid} -> {user_email}")
                
            except Exception as auto_reg_error:
                db.session.rollback()
                return error_response(
                    f'Failed to auto-register nutritionist: {str(auto_reg_error)}. Please contact support.',
                    500
                )
        
        # Get invitations for this nutritionist ONLY - strict filtering
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
            'total': len(invitations),
            'nutritionist_id': nutritionist.id,  # Add for debugging
            'user_uid': user_uid  # Add for debugging
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
