# New Business Rules Implementation - Complete

## Overview

This document describes the implementation of new business rules for the nutritionist-patient relationship and meal plan versioning system.

## 🎯 Business Rules Implemented

### 1. Nutritionist-Patient Relationships
- **One nutritionist can have multiple patients**
  - Nutritionists are now explicit entities in the system
  - Each patient invitation is linked to a specific nutritionist
  - Nutritionists can manage all their patients from a centralized dashboard

### 2. Meal Plan Versioning
- **One patient can have multiple meal plan versions**
  - Each meal plan has a version number (1, 2, 3, etc.)
  - Only one version can be "latest" at a time
  - Patients see only the latest approved version
  - Nutritionists can view and manage all versions

## 🗃️ Database Schema Changes

### New Tables

#### `nutritionists`
```sql
CREATE TABLE nutritionists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firebase_uid VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    license_number VARCHAR(100),
    specialization VARCHAR(200),
    bio TEXT,
    profile_image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT 1,
    is_verified BOOLEAN DEFAULT 0,
    verification_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Updated Tables

#### `meal_plans` - Added Versioning
```sql
-- New columns added:
ALTER TABLE meal_plans ADD COLUMN version INTEGER DEFAULT 1;
ALTER TABLE meal_plans ADD COLUMN is_latest BOOLEAN DEFAULT 1;
ALTER TABLE meal_plans ADD COLUMN parent_plan_id INTEGER REFERENCES meal_plans(id);
ALTER TABLE meal_plans ADD COLUMN nutritionist_id INTEGER REFERENCES nutritionists(id);
```

#### `patient_invitations` - Added Nutritionist Link
```sql
-- New column added:
ALTER TABLE patient_invitations ADD COLUMN nutritionist_id INTEGER REFERENCES nutritionists(id);
```

### Performance Indexes
```sql
CREATE INDEX idx_meal_plans_patient_version ON meal_plans(patient_id, version DESC);
CREATE INDEX idx_meal_plans_patient_latest ON meal_plans(patient_id, is_latest) WHERE is_latest = 1;
CREATE INDEX idx_meal_plans_nutritionist ON meal_plans(nutritionist_id);
CREATE INDEX idx_invitations_nutritionist ON patient_invitations(nutritionist_id);
CREATE INDEX idx_nutritionists_firebase_uid ON nutritionists(firebase_uid);
```

### Versioning Trigger
```sql
CREATE TRIGGER update_meal_plan_latest 
AFTER INSERT ON meal_plans
FOR EACH ROW
WHEN NEW.parent_plan_id IS NOT NULL
BEGIN
    -- Set previous versions to not latest
    UPDATE meal_plans 
    SET is_latest = 0 
    WHERE patient_id = NEW.patient_id 
    AND id != NEW.id 
    AND (parent_plan_id = NEW.parent_plan_id OR id = NEW.parent_plan_id);
    
    -- Ensure new version is latest
    UPDATE meal_plans 
    SET is_latest = 1 
    WHERE id = NEW.id;
END;
```

## 🔄 API Endpoints

### Nutritionist Endpoints (Authenticated)

#### Profile Management
- `POST /api/nutritionist/profile` - Create or update nutritionist profile
- `GET /api/nutritionist/profile` - Get nutritionist profile

#### Dashboard
- `GET /api/nutritionist/dashboard` - Get comprehensive dashboard data
  - Nutritionist stats
  - Pending invitations
  - Patients needing review
  - All patients with their latest meal plans

#### Patient Management
- `GET /api/nutritionist/patients/{id}/meal-plans` - Get all meal plan versions for a patient
- `GET /api/nutritionist/patients/{id}/meal-plans/stats` - Get versioning statistics

#### Meal Plan Versioning
- `POST /api/nutritionist/patients/{id}/meal-plans` - Create new meal plan version
- `POST /api/nutritionist/meal-plans/{id}/versions` - Create version from existing plan
- `POST /api/nutritionist/meal-plans/{id}/approve` - Approve a meal plan version
- `POST /api/nutritionist/meal-plans/compare` - Compare two meal plan versions

#### Data Migration
- `POST /api/nutritionist/migrate-data` - Migrate existing data to new structure

### Patient Endpoints (Public, Token-based)

#### Meal Plan Access (Latest Version Only)
- `GET /api/patient/meal-plan/{token}` - Get latest approved meal plan
- `GET /api/patient/meal-plan/{token}/summary` - Get meal plan summary with nutritional stats

## 🏗️ Backend Implementation

### New Services

#### `NutritionistService`
- Profile management
- Dashboard data aggregation
- Patient relationship management
- Data migration utilities

#### `MealPlanVersioningService`
- Version creation and management
- Version comparison
- Statistics and analytics
- Patient vs nutritionist view handling

### Updated Models

#### `Nutritionist` Model
```python
class Nutritionist(BaseModel):
    # Profile fields
    firebase_uid = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    # ... other fields
    
    # Relationships
    invitations = relationship("PatientInvitation", back_populates="nutritionist")
    meal_plans = relationship("MealPlan", back_populates="nutritionist")
```

#### `MealPlan` Model (Enhanced)
```python
class MealPlan(BaseModel):
    # Existing fields...
    
    # New versioning fields
    version = Column(Integer, default=1)
    is_latest = Column(Boolean, default=True)
    parent_plan_id = Column(Integer, ForeignKey('meal_plans.id'))
    nutritionist_id = Column(Integer, ForeignKey('nutritionists.id'))
    
    # Enhanced relationships
    nutritionist = relationship("Nutritionist", back_populates="meal_plans")
    parent_plan = relationship("MealPlan", remote_side=[id], backref="versions")
    
    # Helper methods
    @staticmethod
    def get_latest_for_patient(patient_id: int)
    
    @staticmethod
    def get_all_versions_for_patient(patient_id: int)
    
    def create_new_version(self, nutritionist_id: int, ...)
```

## 🎨 Frontend Implementation

### New TypeScript Types

#### Core Types
```typescript
interface Nutritionist {
  id: number;
  firebase_uid: string;
  email: string;
  first_name: string;
  last_name: string;
  specialization?: string;
  // ... other fields
}

interface MealPlanVersion {
  id: number;
  patient_id: number;
  nutritionist_id?: number;
  version: number;
  is_latest: boolean;
  parent_plan_id?: number;
  // ... other fields
}
```

#### Dashboard Types
```typescript
interface NutritionistDashboard {
  nutritionist: Nutritionist;
  stats: {
    total_patients: number;
    pending_invitations: number;
    pending_reviews: number;
    total_meal_plans: number;
    active_meal_plans: number;
  };
  pending_invitations: PatientInvitation[];
  pending_reviews: PatientInvitation[];
  patients: PatientWithMealPlans[];
}
```

### New React Hooks

#### `useNutritionistProfile()`
- Profile management
- Create/update nutritionist profile
- Auto-fetch on mount

#### `useNutritionistDashboard()`
- Dashboard data fetching
- Real-time stats
- Patient management overview

#### `usePatientMealPlanHistory(patientId)`
- All meal plan versions for a patient
- Nutritionist view only

#### `useMealPlanVersioning()`
- Version creation operations
- Approval workflow
- Version comparison utilities

#### `usePatientMealPlan(token)`
- Patient-facing meal plan access
- Latest approved version only
- No authentication required (token-based)

## 🔄 Migration Strategy

### Automatic Migration
1. **Database Schema**: Applied via SQL migration script
2. **Existing Data**: Meal plans updated with `version=1, is_latest=1`
3. **API Compatibility**: Old endpoints still work during transition

### Manual Migration Steps
1. **Nutritionist Registration**: Existing users call `POST /api/nutritionist/migrate-data`
2. **Data Linking**: Links existing invitations and meal plans to nutritionist entity
3. **Profile Completion**: Update nutritionist profile information

## 📊 Key Features

### For Nutritionists
1. **Centralized Dashboard**
   - All patients in one view
   - Pending tasks clearly visible
   - Quick access to patient histories

2. **Version Management**
   - Create new versions easily
   - Compare versions side-by-side
   - View complete version history
   - Approval workflow

3. **Patient Insights**
   - Track meal plan evolution
   - Version statistics
   - Patient engagement metrics

### For Patients
1. **Always Current**
   - See only latest approved version
   - No confusion with old versions
   - Seamless updates

2. **Professional Presentation**
   - Nutritionist information included
   - Version number for reference
   - Nutritional summaries

## 🚀 Benefits

### Business Benefits
- **Scalability**: One nutritionist can manage many patients efficiently
- **Traceability**: Complete audit trail of meal plan changes
- **Professionalism**: Clear nutritionist branding and credentials
- **Flexibility**: Easy to update and iterate meal plans

### Technical Benefits
- **Performance**: Optimized with proper indexes
- **Maintainability**: Clear separation of concerns
- **Extensibility**: Easy to add new features
- **Backward Compatibility**: Existing functionality preserved

## 🧪 Testing

### Database Tests
- Schema validation
- Relationship integrity
- Index performance
- Trigger functionality

### API Tests
- Authentication flow
- CRUD operations
- Error handling
- Data validation

### Integration Tests
- End-to-end workflows
- Version management
- Patient access patterns

## 📈 Future Enhancements

### Phase 2 Features
- Meal plan templates
- Bulk patient operations
- Advanced analytics
- Notification system
- Mobile app support

### Advanced Versioning
- Branching and merging
- Collaborative editing
- Automated versioning
- Version approval workflows

---

## ✅ Implementation Status

**Status**: ✅ **COMPLETE**

- ✅ Database schema updated
- ✅ Backend services implemented
- ✅ API endpoints created
- ✅ Frontend types defined
- ✅ React hooks implemented
- ✅ Migration scripts ready
- ✅ Tests passing
- ✅ Documentation complete

The new business rules are now fully implemented and ready for use!
