from flask import Blueprint, request, jsonify
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.services.database_service import db
from app.models.sql_models import (
    PatientInvitation, Patient, MedicalCondition, FoodIntolerance, DietaryPreference,
    PatientMedicalCondition, PatientIntolerance, PatientDietaryPreference
)
from app.services.meal_plan_generator import meal_plan_generator
from app.utils.responses import success_response, error_response

# Public routes - NO AUTH REQUIRED
public_bp = Blueprint('public', __name__, url_prefix='/api/public')

@public_bp.route('/invitations/<token>', methods=['GET'])
def validate_invitation_token(token):
    """Validar token de invitación (endpoint público)."""
    try:
        invitation = db.session.query(PatientInvitation).filter(
            PatientInvitation.token == token
        ).first()
        
        if not invitation:
            return jsonify({
                'valid': False,
                'error': 'Token inválido'
            }), 404
        
        if not invitation.is_valid:
            return jsonify({
                'valid': False,
                'error': 'Token expirado o ya usado'
            }), 400
        
        return jsonify({
            'valid': True,
            'invitation': {
                'invitation_id': invitation.id,
                'email': invitation.email,
                'first_name': invitation.first_name,
                'last_name': invitation.last_name,
                'expires_at': invitation.expires_at.isoformat()
            }
        })
        
    except Exception as e:
        return error_response(f'Error validando token: {str(e)}', 500)

@public_bp.route('/profiles/<token>', methods=['POST'])
def complete_patient_profile(token):
    """Completar perfil del paciente y generar plan automáticamente."""
    try:
        # 1. Validar token
        invitation = db.session.query(PatientInvitation).filter(
            PatientInvitation.token == token
        ).first()
        
        if not invitation or not invitation.is_valid:
            return error_response('Token inválido o expirado', 400)
        
        # 2. Validar datos del formulario
        data = request.get_json()
        if not data:
            return error_response('Datos del perfil requeridos', 400)
        
        # Validar campos obligatorios
        required_fields = ['first_name', 'last_name', 'date_of_birth', 'gender']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'{field} es requerido', 400)
        
        # Validar formato de fecha
        try:
            birth_date = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            # Validar edad razonable (1-120 años)
            age = (datetime.now().date() - birth_date).days / 365.25
            if age < 1 or age > 120:
                return error_response('Fecha de nacimiento inválida', 400)
        except ValueError:
            return error_response('Formato de fecha inválido. Use YYYY-MM-DD', 400)
        
        # Validar género
        if data['gender'] not in ['male', 'female', 'other']:
            return error_response('Valor de género inválido', 400)
        
        # Validar que tenga al menos una condición médica o intolerancia
        medical_conditions = data.get('medical_conditions', [])
        intolerances = data.get('intolerances', [])
        if not medical_conditions and not intolerances:
            return error_response('Debe seleccionar al menos una condición médica o intolerancia', 400)
        
        # 3. Crear paciente
        patient = Patient(
            invitation_id=invitation.id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            date_of_birth=birth_date,
            gender=data['gender'],
            email=data.get('email', invitation.email),
            phone=data.get('phone'),
            additional_notes=data.get('additional_notes'),
            profile_status='approved'  # Auto-aprobado para el flujo público
        )
        
        db.session.add(patient)
        db.session.flush()  # Para obtener el ID del paciente
        
        # 4. Agregar condiciones médicas
        for condition_id in medical_conditions:
            condition = db.session.query(MedicalCondition).filter(
                MedicalCondition.id == condition_id
            ).first()
            if condition:
                patient_condition = PatientMedicalCondition(
                    patient_id=patient.id,
                    condition_id=condition_id
                )
                db.session.add(patient_condition)
        
        # 5. Agregar intolerancias
        for intolerance_id in intolerances:
            intolerance = db.session.query(FoodIntolerance).filter(
                FoodIntolerance.id == intolerance_id
            ).first()
            if intolerance:
                patient_intolerance = PatientIntolerance(
                    patient_id=patient.id,
                    intolerance_id=intolerance_id,
                    severity=data.get('intolerance_severity', 'mild')
                )
                db.session.add(patient_intolerance)
        
        # 6. Agregar preferencias dietéticas
        dietary_preferences = data.get('dietary_preferences', [])
        for preference_id in dietary_preferences:
            preference = db.session.query(DietaryPreference).filter(
                DietaryPreference.id == preference_id
            ).first()
            if preference:
                patient_preference = PatientDietaryPreference(
                    patient_id=patient.id,
                    preference_id=preference_id
                )
                db.session.add(patient_preference)
        
        # 7. Marcar invitación como completada
        invitation.status = 'completed'
        invitation.completed_at = datetime.utcnow()
        
        # 8. Guardar cambios hasta aquí
        db.session.commit()
        
        # 9. Generar plan de comidas automáticamente
        try:
            plan_result = meal_plan_generator.generate_for_new_patient(
                patient_id=patient.id,
                generated_by_uid=invitation.invited_by_uid
            )
            
            return jsonify({
                'success': True,
                'patient_id': patient.id,
                'meal_plan_token': plan_result['token'],
                'meal_plan_link': f'/my-meal-plan/{plan_result["token"]}',
                'message': 'Perfil completado. Tu plan personalizado está listo.',
                'plan_details': {
                    'week_start': plan_result['week_start'],
                    'week_end': plan_result['week_end'],
                    'meal_count': plan_result['meal_count']
                }
            })
            
        except Exception as plan_error:
            # Si falla la generación del plan, devolver éxito del perfil pero notificar el error
            return jsonify({
                'success': True,
                'patient_id': patient.id,
                'meal_plan_token': None,
                'message': 'Perfil completado, pero hubo un problema generando el plan de comidas.',
                'error': f'Error generando plan: {str(plan_error)}'
            })
        
    except IntegrityError as e:
        db.session.rollback()
        return error_response('Error de integridad en los datos', 400)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error completando perfil: {str(e)}', 500)

@public_bp.route('/meal-plans/<token>', methods=['GET'])
def view_patient_meal_plan(token):
    """Ver plan de comidas del paciente usando token público."""
    try:
        plan_data = meal_plan_generator.get_plan_by_token(token)
        
        if not plan_data:
            return error_response('Plan no encontrado o token inválido', 404)
        
        return jsonify(plan_data)
        
    except Exception as e:
        return error_response(f'Error obteniendo plan de comidas: {str(e)}', 500)

@public_bp.route('/catalogs', methods=['GET'])
def get_public_catalogs():
    """Obtener catálogos para el formulario público."""
    try:
        # Obtener condiciones médicas activas
        medical_conditions = db.session.query(MedicalCondition).filter(
            MedicalCondition.is_active == True
        ).all()
        
        # Obtener intolerancias activas
        food_intolerances = db.session.query(FoodIntolerance).filter(
            FoodIntolerance.is_active == True
        ).all()
        
        # Obtener preferencias dietéticas activas
        dietary_preferences = db.session.query(DietaryPreference).filter(
            DietaryPreference.is_active == True
        ).all()
        
        return jsonify({
            'medical_conditions': [mc.to_dict() for mc in medical_conditions],
            'food_intolerances': [fi.to_dict() for fi in food_intolerances],
            'dietary_preferences': [dp.to_dict() for dp in dietary_preferences]
        })
        
    except Exception as e:
        return error_response(f'Error obteniendo catálogos: {str(e)}', 500)
