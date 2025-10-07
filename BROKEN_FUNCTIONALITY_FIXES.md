# Broken Functionality Fixes

## Issues Identified and Fixed

### 1. **Authentication Import Inconsistency**
**Problem**: Some routes were importing `require_auth` from `middleware.auth` while others from `utils.auth_utils`, causing import errors.

**Files Fixed**:
- `/backend/app/routes/invitations.py`
- `/backend/app/routes/meal_plan_workflow.py`

**Changes Made**:
- Standardized all imports to use `require_auth` from `utils.auth_utils`
- Updated all `request.user.get('uid')` calls to use `get_current_user_uid()` helper function
- This ensures consistent authentication handling across all routes

### 2. **Dashboard Filtering Not Using Nutritionist Entity**
**Problem**: Dashboard data was still filtering by `invited_by_uid` instead of using the new `nutritionist_id` foreign key relationship from the business rules implementation.

**Files Fixed**:
- `/backend/app/services/meal_plan_workflow_service.py`

**Changes Made**:
- Updated `get_nutritionist_dashboard_data()` to first get the nutritionist entity by `firebase_uid`
- Changed all database queries to filter by `nutritionist_id` instead of `invited_by_uid`
- This ensures that dashboard data is properly scoped to the nutritionist entity

### 3. **Invitation Service Using Old Firebase Model**
**Problem**: The invitation service was still using Firebase/Firestore models instead of the new SQL models with nutritionist relationships.

**Files Fixed**:
- `/backend/app/services/invitation_service.py`

**Changes Made**:
- Updated imports to use SQL models (`PatientInvitation`, `Patient`, `Nutritionist`)
- Modified `create_invitation()` to set both `invited_by_uid` (backward compatibility) and `nutritionist_id` (new FK)
- Updated all methods to work with SQLAlchemy models instead of Firestore
- Fixed patient profile creation to use SQL models and relationships

### 4. **Invitation Routes Using Old Model Methods**
**Problem**: The invitation routes were calling methods that existed in the old Firebase model but not in the SQL model.

**Files Fixed**:
- `/backend/app/routes/invitations.py`

**Changes Made**:
- Updated all database queries to use SQLAlchemy ORM methods
- Fixed `list_invitations()` to filter by nutritionist entity
- Updated `get_invitation()`, `resend_invitation()`, and `cancel_invitation()` methods
- Added proper nutritionist lookup for access control

### 5. **Workflow Service Invitation Creation**
**Problem**: The workflow service wasn't properly setting the nutritionist relationship when creating invitations.

**Files Fixed**:
- `/backend/app/services/meal_plan_workflow_service.py`

**Changes Made**:
- Added nutritionist entity lookup in `create_workflow_invitation()`
- Set both `invited_by_uid` and `nutritionist_id` when creating invitations
- Updated filtering to use `nutritionist_id` instead of `invited_by_uid`

## Testing Required

After these fixes, the following functionality should be tested:

### Dashboard Testing
1. **Nutritionist Dashboard**: Verify that dashboard data only shows invitations and patients belonging to the logged-in nutritionist
2. **Dashboard Filtering**: Confirm that pending reviews, approved plans, and pending invitations are properly filtered by nutritionist

### Invitation Testing
1. **Create Invitation**: Test creating new invitations with proper nutritionist relationship
2. **List Invitations**: Verify that only invitations from the current nutritionist are shown
3. **Invitation Access**: Test that nutritionists can only access their own invitations
4. **Public Invitation Links**: Verify that invitation tokens work correctly for patient profile completion

### Authentication Testing
1. **Consistent Auth**: Verify that all protected endpoints use the same authentication mechanism
2. **User Context**: Test that `get_current_user_uid()` works consistently across all routes

## Database Migration Notes

The fixes assume that the following migrations have been applied:
- `nutritionist_id` column exists in `patient_invitations` table
- `nutritionist_id` column exists in `meal_plans` table
- Foreign key relationships are properly set up
- Existing data has been migrated to link with nutritionist entities

## Backward Compatibility

The fixes maintain backward compatibility by:
- Keeping `invited_by_uid` fields populated for existing functionality
- Using both old and new filtering approaches where necessary
- Ensuring that existing tokens and links continue to work

## Next Steps

1. **Test thoroughly** with different nutritionist accounts
2. **Verify data isolation** - ensure nutritionists can only see their own data
3. **Check invitation workflow** - from creation to patient completion
4. **Monitor performance** - ensure the new queries are efficient
5. **Update frontend** if any API response formats have changed

## Error Handling Improvements

Added proper error handling for:
- Missing nutritionist entities
- Invalid invitation tokens
- Database transaction failures
- Access control violations

These fixes should resolve the broken functionality related to dashboard filtering and invitation errors after applying the new business rules implementation.
