"""
Routes for patient invitation management.
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from ..middleware.auth import require_auth
from ..utils.responses import success_response, error_response
from ..services.database_service import db
from ..models.sql_models import PatientInvitation, Patient

invitations_bp = Blueprint('invitations', __name__, url_prefix='/api/invitations')

@invitations_bp.route('', methods=['GET'])
@require_auth
def get_invitations():
    """Get all patient invitations for the current nutritionist."""
    try:
        from ..utils.auth_utils import get_current_user_uid
        from ..models.sql_models import Nutritionist
        
        user_uid = get_current_user_uid()
        
        # Get nutritionist first
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        
        # Filter by nutritionist_id to only show invitations belonging to this nutritionist
        query = PatientInvitation.query.filter_by(nutritionist_id=nutritionist.id)
        
        if status:
            query = query.filter(PatientInvitation.status == status)
        
        invitations = query.order_by(PatientInvitation.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Add public_link for pending invitations
        invitation_dicts = []
        for inv in invitations.items:
            inv_dict = inv.to_dict()
            if inv.status == 'pending':
                from app.services.invitation_service import InvitationService
                inv_dict['public_link'] = InvitationService._generate_public_link(inv.token)
            invitation_dicts.append(inv_dict)
        
        return success_response({
            'invitations': invitation_dicts,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': invitations.total,
                'pages': invitations.pages,
                'has_next': invitations.has_next,
                'has_prev': invitations.has_prev
            }
        }, "Invitations retrieved successfully")
        
    except Exception as e:
        return error_response(f"Error retrieving invitations: {str(e)}", 500)

@invitations_bp.route('/stats', methods=['GET'])
@require_auth
def get_invitation_stats():
    """Get invitation statistics for the current nutritionist."""
    try:
        from ..utils.auth_utils import get_current_user_uid
        from ..models.sql_models import Nutritionist
        
        user_uid = get_current_user_uid()
        
        # Get nutritionist first
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Get counts for invitations created by this nutritionist
        base_query = PatientInvitation.query.filter_by(nutritionist_id=nutritionist.id)
        
        total = base_query.count()
        pending = base_query.filter_by(status='pending').count()
        completed = base_query.filter_by(status='completed').count()
        expired = base_query.filter(
            PatientInvitation.status == 'pending',
            PatientInvitation.expires_at < datetime.utcnow()
        ).count()
        
        stats = {
            'total': total,
            'pending': pending,
            'completed': completed,
            'expired': expired
        }
        
        return success_response({'stats': stats}, "Statistics retrieved successfully")
        
    except Exception as e:
        return error_response(f"Error retrieving statistics: {str(e)}", 500)

@invitations_bp.route('', methods=['POST'])
@require_auth
def create_invitation():
    """Create a new patient invitation."""
    try:
        from ..utils.auth_utils import get_current_user_uid
        from ..models.sql_models import Nutritionist
        
        data = request.get_json()
        user_uid = get_current_user_uid()
        
        # Get nutritionist first
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Validate required fields
        required_fields = ['email']
        for field in required_fields:
            if not data.get(field):
                return error_response(f"Missing required field: {field}", 400)
        
        # Check if invitation already exists for this email from this nutritionist
        existing = PatientInvitation.query.filter_by(
            email=data['email'], 
            nutritionist_id=nutritionist.id,
            status='pending'
        ).first()
        
        if existing and existing.is_valid:
            return error_response("Active invitation already exists for this email", 400)
        
        # Create new invitation
        invitation = PatientInvitation(
            email=data['email'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            invited_by_uid=user_uid,  # Keep for backward compatibility
            nutritionist_id=nutritionist.id  # Set the proper nutritionist relationship
        )
        
        db.session.add(invitation)
        db.session.commit()
        
        # Include public_link in response
        invitation_dict = invitation.to_dict()
        from app.services.invitation_service import InvitationService
        invitation_dict['public_link'] = InvitationService._generate_public_link(invitation.token)
        
        return success_response(invitation_dict, "Invitation created successfully", 201)
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Error creating invitation: {str(e)}", 500)

@invitations_bp.route('/<int:invitation_id>', methods=['GET'])
@require_auth
def get_invitation(invitation_id):
    """Get a specific invitation for the current nutritionist."""
    try:
        from ..utils.auth_utils import get_current_user_uid
        from ..models.sql_models import Nutritionist
        
        user_uid = get_current_user_uid()
        
        # Get nutritionist first
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Get invitation and verify ownership
        invitation = PatientInvitation.query.filter_by(
            id=invitation_id,
            nutritionist_id=nutritionist.id
        ).first()
        
        if not invitation:
            return error_response("Invitation not found", 404)
        
        return success_response(invitation.to_dict(), "Invitation retrieved successfully")
        
    except Exception as e:
        return error_response(f"Error retrieving invitation: {str(e)}", 500)

@invitations_bp.route('/<int:invitation_id>', methods=['PUT'])
@require_auth
def update_invitation(invitation_id):
    """Update an invitation for the current nutritionist."""
    try:
        from ..utils.auth_utils import get_current_user_uid
        from ..models.sql_models import Nutritionist
        
        user_uid = get_current_user_uid()
        
        # Get nutritionist first
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Get invitation and verify ownership
        invitation = PatientInvitation.query.filter_by(
            id=invitation_id,
            nutritionist_id=nutritionist.id
        ).first()
        
        if not invitation:
            return error_response("Invitation not found", 404)
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'status']
        for field in allowed_fields:
            if field in data:
                setattr(invitation, field, data[field])
        
        if data.get('status') == 'completed':
            invitation.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return success_response(invitation.to_dict(), "Invitation updated successfully")
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Error updating invitation: {str(e)}", 500)

@invitations_bp.route('/<int:invitation_id>', methods=['DELETE'])
@require_auth
def delete_invitation(invitation_id):
    """Delete an invitation for the current nutritionist."""
    try:
        from ..utils.auth_utils import get_current_user_uid
        from ..models.sql_models import Nutritionist
        
        user_uid = get_current_user_uid()
        
        # Get nutritionist first
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Get invitation and verify ownership
        invitation = PatientInvitation.query.filter_by(
            id=invitation_id,
            nutritionist_id=nutritionist.id
        ).first()
        
        if not invitation:
            return error_response("Invitation not found", 404)
        
        # Check if invitation has been completed
        if invitation.status == 'completed':
            return error_response("Cannot delete completed invitation", 400)
        
        db.session.delete(invitation)
        db.session.commit()
        
        return success_response({}, "Invitation deleted successfully")
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Error deleting invitation: {str(e)}", 500)

@invitations_bp.route('/token/<token>', methods=['GET'])
def get_invitation_by_token(token):
    """Get invitation by token (public endpoint for patient registration)."""
    try:
        invitation = PatientInvitation.query.filter_by(token=token).first()
        
        if not invitation:
            return error_response("Invitation not found", 404)
        
        if not invitation.is_valid:
            return error_response("Invitation has expired or is no longer valid", 400)
        
        # Return limited information for security
        return success_response({
            'token': invitation.token,
            'email': invitation.email,
            'first_name': invitation.first_name,
            'last_name': invitation.last_name,
            'expires_at': invitation.expires_at.isoformat()
        }, "Invitation retrieved successfully")
        
    except Exception as e:
        return error_response(f"Error retrieving invitation: {str(e)}", 500)

@invitations_bp.route('/resend/<int:invitation_id>', methods=['POST'])
@require_auth
def resend_invitation(invitation_id):
    """Resend an invitation (extend expiry) for the current nutritionist."""
    try:
        from ..utils.auth_utils import get_current_user_uid
        from ..models.sql_models import Nutritionist
        
        user_uid = get_current_user_uid()
        
        # Get nutritionist first
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Get invitation and verify ownership
        invitation = PatientInvitation.query.filter_by(
            id=invitation_id,
            nutritionist_id=nutritionist.id
        ).first()
        
        if not invitation:
            return error_response("Invitation not found", 404)
        
        if invitation.status == 'completed':
            return error_response("Cannot resend completed invitation", 400)
        
        # Extend expiry date
        invitation.expires_at = datetime.utcnow() + timedelta(days=7)
        invitation.status = 'pending'
        
        db.session.commit()
        
        # Include public_link in response
        invitation_dict = invitation.to_dict()
        from app.services.invitation_service import InvitationService
        invitation_dict['public_link'] = InvitationService._generate_public_link(invitation.token)
        
        return success_response(invitation_dict, "Invitation resent successfully")
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Error resending invitation: {str(e)}", 500)

@invitations_bp.route('/regenerate/<int:invitation_id>', methods=['POST'])
@require_auth
def regenerate_invitation_link(invitation_id):
    """Regenerate invitation token and link."""
    try:
        from ..utils.auth_utils import get_current_user_uid
        from ..models.sql_models import Nutritionist
        
        user_uid = get_current_user_uid()
        
        # Get nutritionist first
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Get invitation and verify ownership
        invitation = PatientInvitation.query.filter_by(
            id=invitation_id,
            nutritionist_id=nutritionist.id
        ).first()
        
        if not invitation:
            return error_response("Invitation not found", 404)
        
        if invitation.status == 'completed':
            return error_response("Cannot regenerate completed invitation", 400)
        
        # Regenerate token and extend expiry
        invitation.regenerate_token()
        
        db.session.commit()
        
        # Include the new public link in response
        invitation_dict = invitation.to_dict()
        from app.services.invitation_service import InvitationService
        invitation_dict['public_link'] = InvitationService._generate_public_link(invitation.token)
        
        return success_response(invitation_dict, "Invitation link regenerated successfully")
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Error regenerating invitation: {str(e)}", 500)
