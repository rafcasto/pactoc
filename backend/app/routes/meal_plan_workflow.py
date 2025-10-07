"""
Routes for meal plan workflow system.
Handles the dynamic link routing and workflow management.
"""
from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
from ..utils.auth_utils import require_auth, get_current_user_uid
from ..utils.responses import success_response, error_response
from ..services.meal_plan_workflow_service import MealPlanWorkflowService

workflow_bp = Blueprint('meal_plan_workflow', __name__, url_prefix='/api/workflow')

# Nutritionist Routes (authenticated)

@workflow_bp.route('/invitations', methods=['POST'])
@require_auth
def create_workflow_invitation():
    """Create a new meal plan workflow invitation."""
    try:
        data = request.get_json()
        user_uid = get_current_user_uid()
        
        # Validate required fields
        if not data.get('email'):
            return error_response("Email is required", 400)
        if not data.get('patient_name'):
            return error_response("Patient name is required", 400)
        
        success, result, error = MealPlanWorkflowService.create_workflow_invitation(
            email=data['email'],
            patient_name=data['patient_name'],
            invited_by_uid=user_uid
        )
        
        if success:
            return success_response(result, "Workflow invitation created successfully", 201)
        else:
            return error_response(error, 400)
    
    except Exception as e:
        return error_response(f"Error creating workflow invitation: {str(e)}", 500)

@workflow_bp.route('/dashboard', methods=['GET'])
@require_auth
def get_nutritionist_dashboard():
    """Get dashboard data for nutritionist."""
    try:
        user_uid = get_current_user_uid()
        
        success, dashboard_data, error = MealPlanWorkflowService.get_nutritionist_dashboard_data(user_uid)
        
        if success:
            return success_response(dashboard_data, "Dashboard data retrieved successfully")
        else:
            return error_response(error, 400)
    
    except Exception as e:
        return error_response(f"Error getting dashboard data: {str(e)}", 500)

@workflow_bp.route('/approve/<int:invitation_id>', methods=['POST'])
@require_auth
def approve_meal_plan():
    """Approve meal plan for a patient."""
    try:
        data = request.get_json() or {}
        user_uid = get_current_user_uid()
        invitation_id = request.view_args['invitation_id']
        
        success, result, error = MealPlanWorkflowService.approve_meal_plan(
            invitation_id=invitation_id,
            approved_by_uid=user_uid,
            meal_plan_data=data
        )
        
        if success:
            return success_response(result, "Meal plan approved successfully")
        else:
            return error_response(error, 400)
    
    except Exception as e:
        return error_response(f"Error approving meal plan: {str(e)}", 500)

# Public Routes (no authentication required)

@workflow_bp.route('/patient/<token>', methods=['GET'])
def get_dynamic_link_content(token):
    """Get content for the dynamic patient link based on invitation status."""
    try:
        success, content_data, error = MealPlanWorkflowService.get_dynamic_link_content(token)
        
        if success:
            return success_response(content_data, "Content retrieved successfully")
        else:
            return error_response(error, 404 if "not found" in error.lower() else 400)
    
    except Exception as e:
        return error_response(f"Error getting dynamic link content: {str(e)}", 500)

@workflow_bp.route('/patient/<token>/submit', methods=['POST'])
def submit_patient_form(token):
    """Submit patient form data."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'date_of_birth', 'gender']
        for field in required_fields:
            if not data.get(field):
                return error_response(f"Missing required field: {field}", 400)
        
        success, result, error = MealPlanWorkflowService.submit_patient_form(token, data)
        
        if success:
            return success_response(result, "Form submitted successfully")
        else:
            return error_response(error, 400)
    
    except Exception as e:
        return error_response(f"Error submitting form: {str(e)}", 500)

@workflow_bp.route('/patient/<token>/pdf', methods=['GET'])
def export_meal_plan_pdf(token):
    """Export meal plan as PDF."""
    try:
        success, pdf_content, filename, error = MealPlanWorkflowService.export_meal_plan_pdf(token)
        
        if success:
            return send_file(
                BytesIO(pdf_content),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            return error_response(error, 400)
    
    except Exception as e:
        return error_response(f"Error exporting PDF: {str(e)}", 500)

@workflow_bp.route('/patient/<token>/print', methods=['GET'])
def get_meal_plan_print_view(token):
    """Get meal plan in print-optimized format."""
    try:
        success, content_data, error = MealPlanWorkflowService.get_dynamic_link_content(token)
        
        if not success or content_data['content_type'] != 'meal_plan':
            return error_response(error or "Meal plan not available for printing", 400)
        
        # Return data optimized for print view
        print_data = content_data['data']
        print_data['print_optimized'] = True
        
        return success_response(print_data, "Print view data retrieved successfully")
    
    except Exception as e:
        return error_response(f"Error getting print view: {str(e)}", 500)