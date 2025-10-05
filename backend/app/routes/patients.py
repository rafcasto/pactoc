from flask import Blueprint, request, jsonify
from ..middleware.auth import require_auth
from ..models.patient import Patient
from ..utils.responses import success_response, error_response

patients_bp = Blueprint('patients', __name__, url_prefix='/api/patients')

@patients_bp.route('/', methods=['GET'])
@require_auth
def list_patients():
    """Get all patients with optional filters."""
    try:
        # Get query parameters
        profile_status = request.args.get('profile_status')  # pending_review, approved
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        search = request.args.get('search')  # Search by name or email
        
        # Build filters
        filters = {'is_active': is_active}
        if profile_status:
            filters['profile_status'] = profile_status
        
        patients = Patient.get_all(filters)
        
        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            patients = [
                p for p in patients 
                if (search_lower in p.get('first_name', '').lower() or 
                    search_lower in p.get('last_name', '').lower() or
                    search_lower in p.get('email', '').lower())
            ]
        
        # Add summary data
        for patient in patients:
            # Count conditions, intolerances, preferences
            patient_details = Patient.get_with_conditions_and_preferences(patient['id'])
            if patient_details:
                patient['conditions_count'] = len(patient_details.get('medical_conditions', []))
                patient['intolerances_count'] = len(patient_details.get('intolerances', []))
                patient['preferences_count'] = len(patient_details.get('dietary_preferences', []))
        
        return success_response({
            'patients': patients,
            'total': len(patients)
        })
        
    except Exception as e:
        return error_response(f'Error retrieving patients: {str(e)}', 500)

@patients_bp.route('/<patient_id>', methods=['GET'])
@require_auth
def get_patient(patient_id):
    """Get patient details with conditions and preferences."""
    try:
        patient = Patient.get_with_conditions_and_preferences(patient_id)
        
        if not patient:
            return error_response('Patient not found', 404)
        
        return success_response({'patient': patient})
        
    except Exception as e:
        return error_response(f'Error retrieving patient: {str(e)}', 500)

@patients_bp.route('/<patient_id>', methods=['PUT'])
@require_auth
def update_patient(patient_id):
    """Update patient information."""
    try:
        data = request.get_json()
        
        if not data:
            return error_response('Update data is required', 400)
        
        # Check if patient exists
        patient = Patient.get_by_id(patient_id)
        if not patient:
            return error_response('Patient not found', 404)
        
        # Update patient
        success = Patient.update(patient_id, data)
        
        if not success:
            return error_response('Error updating patient', 500)
        
        # Get updated patient
        updated_patient = Patient.get_with_conditions_and_preferences(patient_id)
        
        return success_response({
            'patient': updated_patient
        }, 'Patient updated successfully')
        
    except Exception as e:
        return error_response(f'Error updating patient: {str(e)}', 500)

@patients_bp.route('/<patient_id>/status', methods=['PUT'])
@require_auth
def update_patient_status(patient_id):
    """Update patient profile status (approve/reject)."""
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return error_response('Status is required', 400)
        
        status = data['status']
        if status not in ['pending_review', 'approved']:
            return error_response('Invalid status value', 400)
        
        # Check if patient exists
        patient = Patient.get_by_id(patient_id)
        if not patient:
            return error_response('Patient not found', 404)
        
        # Update status
        update_data = {'profile_status': status}
        if status == 'approved':
            update_data['approved_at'] = request.user.get('uid')  # Store who approved
        
        success = Patient.update(patient_id, update_data)
        
        if not success:
            return error_response('Error updating patient status', 500)
        
        return success_response(message=f'Patient status updated to {status}')
        
    except Exception as e:
        return error_response(f'Error updating patient status: {str(e)}', 500)

@patients_bp.route('/<patient_id>', methods=['DELETE'])
@require_auth
def delete_patient(patient_id):
    """Soft delete patient (set is_active to False)."""
    try:
        # Check if patient exists
        patient = Patient.get_by_id(patient_id)
        if not patient:
            return error_response('Patient not found', 404)
        
        # Soft delete
        success = Patient.delete(patient_id)
        
        if not success:
            return error_response('Error deleting patient', 500)
        
        return success_response(message='Patient deleted successfully')
        
    except Exception as e:
        return error_response(f'Error deleting patient: {str(e)}', 500)

@patients_bp.route('/<patient_id>/conditions', methods=['POST'])
@require_auth
def add_patient_condition(patient_id):
    """Add medical condition to patient."""
    try:
        data = request.get_json()
        
        if not data or not data.get('condition_id'):
            return error_response('Condition ID is required', 400)
        
        # Check if patient exists
        patient = Patient.get_by_id(patient_id)
        if not patient:
            return error_response('Patient not found', 404)
        
        # Add condition to subcollection
        from ..services.firebase_service import FirebaseService
        from datetime import datetime
        
        db = FirebaseService.get_firestore()
        db.collection(f'patients/{patient_id}/medical_conditions').add({
            'condition_id': data['condition_id'],
            'condition_name': data.get('condition_name', ''),
            'notes': data.get('notes', ''),
            'added_at': datetime.utcnow()
        })
        
        return success_response(message='Condition added successfully')
        
    except Exception as e:
        return error_response(f'Error adding condition: {str(e)}', 500)

@patients_bp.route('/<patient_id>/conditions/<condition_doc_id>', methods=['DELETE'])
@require_auth
def remove_patient_condition(patient_id, condition_doc_id):
    """Remove medical condition from patient."""
    try:
        from ..services.firebase_service import FirebaseService
        
        db = FirebaseService.get_firestore()
        db.collection(f'patients/{patient_id}/medical_conditions').document(condition_doc_id).delete()
        
        return success_response(message='Condition removed successfully')
        
    except Exception as e:
        return error_response(f'Error removing condition: {str(e)}', 500)

@patients_bp.route('/stats', methods=['GET'])
@require_auth
def get_patients_stats():
    """Get patient statistics."""
    try:
        all_patients = Patient.get_all()
        
        stats = {
            'total': len(all_patients),
            'active': len([p for p in all_patients if p.get('is_active', True)]),
            'pending_review': len([p for p in all_patients if p.get('profile_status') == 'pending_review']),
            'approved': len([p for p in all_patients if p.get('profile_status') == 'approved']),
            'inactive': len([p for p in all_patients if not p.get('is_active', True)])
        }
        
        return success_response({'stats': stats})
        
    except Exception as e:
        return error_response(f'Error retrieving stats: {str(e)}', 500)
