from flask import Blueprint, request, jsonify
from ..middleware.auth import require_auth
from ..models.sql_models import Patient, PatientInvitation, Nutritionist
from ..utils.responses import success_response, error_response
from ..utils.auth_utils import get_current_user_uid
from ..services.database_service import db

patients_bp = Blueprint('patients', __name__, url_prefix='/api/patients')

@patients_bp.route('/', methods=['GET'])
@require_auth
def list_patients():
    """Get all patients for the current nutritionist with optional filters."""
    try:
        user_uid = get_current_user_uid()
        
        # Get nutritionist first
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Get query parameters
        profile_status = request.args.get('profile_status')  # pending_review, approved
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        search = request.args.get('search')  # Search by name or email
        
        # Build query to get patients for this nutritionist
        query = db.session.query(Patient)\
            .join(PatientInvitation, Patient.invitation_id == PatientInvitation.id)\
            .filter(PatientInvitation.nutritionist_id == nutritionist.id)
        
        # Apply filters
        if is_active is not None:
            query = query.filter(Patient.is_active == is_active)
        
        if profile_status:
            query = query.filter(Patient.profile_status == profile_status)
        
        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            query = query.filter(
                db.or_(
                    Patient.first_name.ilike(f'%{search_lower}%'),
                    Patient.last_name.ilike(f'%{search_lower}%'),
                    Patient.email.ilike(f'%{search_lower}%')
                )
            )
        
        patients = query.all()
        
        # Convert to dictionaries with relation data
        patients_data = []
        for patient in patients:
            patient_dict = patient.to_dict(include_relations=True)
            patients_data.append(patient_dict)
        
        return success_response({
            'patients': patients_data,
            'total': len(patients_data)
        })
        
    except Exception as e:
        return error_response(f'Error retrieving patients: {str(e)}', 500)

@patients_bp.route('/<int:patient_id>', methods=['GET'])
@require_auth
def get_patient(patient_id):
    """Get patient details with conditions and preferences."""
    try:
        user_uid = get_current_user_uid()
        
        # Get nutritionist first
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Get patient and verify ownership
        patient = db.session.query(Patient)\
            .join(PatientInvitation, Patient.invitation_id == PatientInvitation.id)\
            .filter(
                Patient.id == patient_id,
                PatientInvitation.nutritionist_id == nutritionist.id
            ).first()
        
        if not patient:
            return error_response('Patient not found', 404)
        
        return success_response({'patient': patient.to_dict(include_relations=True)})
        
    except Exception as e:
        return error_response(f'Error retrieving patient: {str(e)}', 500)

@patients_bp.route('/<int:patient_id>', methods=['PUT'])
@require_auth
def update_patient(patient_id):
    """Update patient information."""
    try:
        user_uid = get_current_user_uid()
        data = request.get_json()
        
        if not data:
            return error_response('Update data is required', 400)
        
        # Get nutritionist first
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Get patient and verify ownership
        patient = db.session.query(Patient)\
            .join(PatientInvitation, Patient.invitation_id == PatientInvitation.id)\
            .filter(
                Patient.id == patient_id,
                PatientInvitation.nutritionist_id == nutritionist.id
            ).first()
        
        if not patient:
            return error_response('Patient not found', 404)
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 
                         'email', 'phone', 'additional_notes', 'profile_status']
        
        for field in allowed_fields:
            if field in data:
                setattr(patient, field, data[field])
        
        # Update timestamp
        patient.updated_at = db.func.now()
        
        db.session.commit()
        
        return success_response({
            'patient': patient.to_dict(include_relations=True)
        }, 'Patient updated successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error updating patient: {str(e)}', 500)

@patients_bp.route('/<int:patient_id>/status', methods=['PUT'])
@require_auth
def update_patient_status(patient_id):
    """Update patient profile status (approve/reject)."""
    try:
        user_uid = get_current_user_uid()
        data = request.get_json()
        
        if not data or 'status' not in data:
            return error_response('Status is required', 400)
        
        status = data['status']
        if status not in ['pending_review', 'approved']:
            return error_response('Invalid status value', 400)
        
        # Get nutritionist first
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Get patient and verify ownership
        patient = db.session.query(Patient)\
            .join(PatientInvitation, Patient.invitation_id == PatientInvitation.id)\
            .filter(
                Patient.id == patient_id,
                PatientInvitation.nutritionist_id == nutritionist.id
            ).first()
        
        if not patient:
            return error_response('Patient not found', 404)
        
        # Update status
        patient.profile_status = status
        patient.updated_at = db.func.now()
        
        db.session.commit()
        
        return success_response(message=f'Patient status updated to {status}')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error updating patient status: {str(e)}', 500)

@patients_bp.route('/<int:patient_id>', methods=['DELETE'])
@require_auth
def delete_patient(patient_id):
    """Soft delete patient (set is_active to False)."""
    try:
        user_uid = get_current_user_uid()
        
        # Get nutritionist first
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Get patient and verify ownership
        patient = db.session.query(Patient)\
            .join(PatientInvitation, Patient.invitation_id == PatientInvitation.id)\
            .filter(
                Patient.id == patient_id,
                PatientInvitation.nutritionist_id == nutritionist.id
            ).first()
        
        if not patient:
            return error_response('Patient not found', 404)
        
        # Soft delete
        patient.is_active = False
        patient.updated_at = db.func.now()
        
        db.session.commit()
        
        return success_response(message='Patient deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error deleting patient: {str(e)}', 500)

@patients_bp.route('/<int:patient_id>/conditions', methods=['POST'])
@require_auth
def add_patient_condition(patient_id):
    """Add medical condition to patient."""
    try:
        user_uid = get_current_user_uid()
        data = request.get_json()
        
        if not data or not data.get('condition_id'):
            return error_response('Condition ID is required', 400)
        
        # Get nutritionist first
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Get patient and verify ownership
        patient = db.session.query(Patient)\
            .join(PatientInvitation, Patient.invitation_id == PatientInvitation.id)\
            .filter(
                Patient.id == patient_id,
                PatientInvitation.nutritionist_id == nutritionist.id
            ).first()
        
        if not patient:
            return error_response('Patient not found', 404)
        
        # Add condition using SQL model
        from ..models.sql_models import PatientMedicalCondition
        
        condition = PatientMedicalCondition(
            patient_id=patient_id,
            condition_id=data['condition_id'],
            notes=data.get('notes', '')
        )
        
        db.session.add(condition)
        db.session.commit()
        
        return success_response(message='Condition added successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error adding condition: {str(e)}', 500)

@patients_bp.route('/<int:patient_id>/conditions/<int:condition_id>', methods=['DELETE'])
@require_auth
def remove_patient_condition(patient_id, condition_id):
    """Remove medical condition from patient."""
    try:
        user_uid = get_current_user_uid()
        
        # Get nutritionist first
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Get patient and verify ownership
        patient = db.session.query(Patient)\
            .join(PatientInvitation, Patient.invitation_id == PatientInvitation.id)\
            .filter(
                Patient.id == patient_id,
                PatientInvitation.nutritionist_id == nutritionist.id
            ).first()
        
        if not patient:
            return error_response('Patient not found', 404)
        
        # Remove condition using SQL model
        from ..models.sql_models import PatientMedicalCondition
        
        condition = PatientMedicalCondition.query.filter_by(
            patient_id=patient_id,
            id=condition_id
        ).first()
        
        if not condition:
            return error_response('Condition not found', 404)
        
        db.session.delete(condition)
        db.session.commit()
        
        return success_response(message='Condition removed successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error removing condition: {str(e)}', 500)

@patients_bp.route('/stats', methods=['GET'])
@require_auth
def get_patients_stats():
    """Get patient statistics for the current nutritionist."""
    try:
        user_uid = get_current_user_uid()
        
        # Get nutritionist first
        nutritionist = Nutritionist.query.filter_by(firebase_uid=user_uid).first()
        if not nutritionist:
            return error_response('Nutritionist not found', 404)
        
        # Get all patients for this nutritionist
        patients = db.session.query(Patient)\
            .join(PatientInvitation, Patient.invitation_id == PatientInvitation.id)\
            .filter(PatientInvitation.nutritionist_id == nutritionist.id).all()
        
        stats = {
            'total': len(patients),
            'active': len([p for p in patients if p.is_active]),
            'pending_review': len([p for p in patients if p.profile_status == 'pending_review']),
            'approved': len([p for p in patients if p.profile_status == 'approved']),
            'inactive': len([p for p in patients if not p.is_active])
        }
        
        return success_response({'stats': stats})
        
    except Exception as e:
        return error_response(f'Error retrieving stats: {str(e)}', 500)
