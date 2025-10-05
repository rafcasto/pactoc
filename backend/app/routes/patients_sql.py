"""
Routes for patient management.
"""
from flask import Blueprint, request
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from ..middleware.auth import require_auth
from ..utils.responses import success_response, error_response
from ..services.database_service import db
from ..models.sql_models import (
    Patient, PatientInvitation, MedicalCondition, FoodIntolerance, 
    DietaryPreference, PatientMedicalCondition, PatientIntolerance, 
    PatientDietaryPreference
)

patients_bp = Blueprint('patients_sql', __name__, url_prefix='/patients')

@patients_bp.route('', methods=['GET'])
@require_auth
def get_patients():
    """Get all patients."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status') or request.args.get('profile_status')  # Support both parameter names
        search = request.args.get('search')
        
        query = Patient.query
        
        if status:
            # Handle potential truncated enum values in database
            if status == 'pending_review':
                # Try both the full and truncated versions for backwards compatibility
                query = query.filter(
                    (Patient.profile_status == 'pending_review') | 
                    (Patient.profile_status == 'pending_rev')
                )
            else:
                query = query.filter(Patient.profile_status == status)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Patient.first_name.ilike(search_filter)) |
                (Patient.last_name.ilike(search_filter)) |
                (Patient.email.ilike(search_filter))
            )
        
        patients = query.order_by(Patient.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return success_response({
            'patients': [patient.to_dict(include_relations=True) for patient in patients.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': patients.total,
                'pages': patients.pages,
                'has_next': patients.has_next,
                'has_prev': patients.has_prev
            }
        }, "Patients retrieved successfully")
        
    except Exception as e:
        return error_response(f"Error retrieving patients: {str(e)}", 500)

@patients_bp.route('', methods=['POST'])
def create_patient():
    """Create a new patient (public endpoint for registration)."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['invitation_token', 'first_name', 'last_name', 'date_of_birth', 'gender']
        for field in required_fields:
            if not data.get(field):
                return error_response(f"Missing required field: {field}", 400)
        
        # Verify invitation token
        invitation = PatientInvitation.query.filter_by(token=data['invitation_token']).first()
        if not invitation or not invitation.is_valid:
            return error_response("Invalid or expired invitation token", 400)
        
        # Check if patient already exists for this invitation
        existing_patient = Patient.query.filter_by(invitation_id=invitation.id).first()
        if existing_patient:
            return error_response("Patient already registered for this invitation", 400)
        
        # Parse date_of_birth
        try:
            date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return error_response("Invalid date format for date_of_birth. Use YYYY-MM-DD", 400)
        
        # Create new patient
        patient = Patient(
            invitation_id=invitation.id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            date_of_birth=date_of_birth,
            gender=data['gender'],
            email=data.get('email'),
            phone=data.get('phone'),
            additional_notes=data.get('additional_notes')
        )
        
        db.session.add(patient)
        
        # Mark invitation as completed
        invitation.status = 'completed'
        invitation.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return success_response(patient.to_dict(), "Patient created successfully", 201)
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Error creating patient: {str(e)}", 500)

@patients_bp.route('/<int:patient_id>', methods=['GET'])
@require_auth
def get_patient(patient_id):
    """Get a specific patient."""
    try:
        patient = Patient.query.get_or_404(patient_id)
        return success_response(patient.to_dict(include_relations=True), "Patient retrieved successfully")
        
    except Exception as e:
        return error_response(f"Error retrieving patient: {str(e)}", 500)

@patients_bp.route('/<int:patient_id>', methods=['PUT'])
@require_auth
def update_patient(patient_id):
    """Update a patient."""
    try:
        patient = Patient.query.get_or_404(patient_id)
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'email', 'phone', 'profile_status', 'additional_notes', 'is_active']
        for field in allowed_fields:
            if field in data:
                value = data[field]
                # Handle truncated enum mapping for profile_status
                if field == 'profile_status' and value == 'pending_review':
                    # Try to use full value, but database might have truncated version
                    try:
                        setattr(patient, field, value)
                    except:
                        # Fallback to truncated version if full version fails
                        setattr(patient, field, 'pending_rev')
                else:
                    setattr(patient, field, value)
        
        # Handle date_of_birth separately
        if 'date_of_birth' in data:
            try:
                patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            except ValueError:
                return error_response("Invalid date format for date_of_birth. Use YYYY-MM-DD", 400)
        
        # Handle gender separately
        if 'gender' in data:
            if data['gender'] in ['male', 'female', 'other']:
                patient.gender = data['gender']
            else:
                return error_response("Invalid gender value. Use 'male', 'female', or 'other'", 400)
        
        db.session.commit()
        
        return success_response(patient.to_dict(include_relations=True), "Patient updated successfully")
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(f"Error updating patient: {str(e)}", 500)
