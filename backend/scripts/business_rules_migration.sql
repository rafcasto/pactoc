-- SQL script to implement new business rules for nutritionist-patient relationships
-- and meal plan versioning

-- 1. Create nutritionists table
CREATE TABLE IF NOT EXISTS nutritionists (
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

-- 2. Add versioning columns to meal_plans table
ALTER TABLE meal_plans ADD COLUMN version INTEGER DEFAULT 1;
ALTER TABLE meal_plans ADD COLUMN is_latest BOOLEAN DEFAULT 1;
ALTER TABLE meal_plans ADD COLUMN parent_plan_id INTEGER REFERENCES meal_plans(id);
ALTER TABLE meal_plans ADD COLUMN nutritionist_id INTEGER REFERENCES nutritionists(id);

-- 3. Add nutritionist_id to patient_invitations table
ALTER TABLE patient_invitations ADD COLUMN nutritionist_id INTEGER REFERENCES nutritionists(id);

-- 4. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_meal_plans_patient_version ON meal_plans(patient_id, version DESC);
CREATE INDEX IF NOT EXISTS idx_meal_plans_patient_latest ON meal_plans(patient_id, is_latest) WHERE is_latest = 1;
CREATE INDEX IF NOT EXISTS idx_meal_plans_nutritionist ON meal_plans(nutritionist_id);
CREATE INDEX IF NOT EXISTS idx_invitations_nutritionist ON patient_invitations(nutritionist_id);
CREATE INDEX IF NOT EXISTS idx_nutritionists_firebase_uid ON nutritionists(firebase_uid);

-- 5. Migrate existing data
UPDATE meal_plans 
SET version = 1, is_latest = 1 
WHERE version IS NULL OR is_latest IS NULL;

-- 6. Create a trigger to maintain is_latest flag
CREATE TRIGGER IF NOT EXISTS update_meal_plan_latest 
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
