// Updated types for new business rules: nutritionist entities and meal plan versioning

export interface Nutritionist {
  id: number;
  firebase_uid: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  license_number?: string;
  specialization?: string;
  bio?: string;
  profile_image_url?: string;
  is_active: boolean;
  is_verified: boolean;
  verification_date?: string;
  created_at: string;
  updated_at: string;
  
  // Relationship counts (when include_relations=true)
  total_patients?: number;
  active_meal_plans?: number;
  total_invitations?: number;
}

export interface MealPlanVersion {
  id: number;
  patient_id: number;
  nutritionist_id?: number;
  plan_name: string;
  start_date: string;
  end_date: string;
  status: 'draft' | 'approved' | 'sent';
  notes?: string;
  generated_by_uid: string;
  approved_by_uid?: string;
  approved_at?: string;
  
  // Versioning fields
  version: number;
  is_latest: boolean;
  parent_plan_id?: number;
  
  created_at: string;
  updated_at: string;
  
  // Relationships (when include_relations=true)
  meals?: MealPlanMeal[];
  nutritionist?: {
    name: string;
    email: string;
    specialization?: string;
  };
  parent_plan?: {
    id: number;
    version: number;
    plan_name: string;
  };
  total_versions?: number;
}

export interface MealPlanMeal {
  id: number;
  plan_id: number;
  recipe_id: number;
  recipe_name?: string;
  day_of_week: 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday';
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  scheduled_time?: string; // HH:MM format
  servings: number;
  calories_per_serving?: number;
}

export interface PatientWithMealPlans {
  id: number;
  first_name: string;
  last_name: string;
  email?: string;
  date_of_birth: string;
  gender: 'male' | 'female' | 'other';
  profile_status: 'pending_review' | 'approved';
  invitation_id: number;
  
  // Medical information
  conditions_count?: number;
  intolerances_count?: number;
  preferences_count?: number;
  medical_conditions?: Array<{
    id: number;
    condition_name: string;
    notes?: string;
  }>;
  intolerances?: Array<{
    id: number;
    intolerance_name: string;
    severity: 'mild' | 'moderate' | 'severe';
    notes?: string;
  }>;
  dietary_preferences?: Array<{
    id: number;
    preference_name: string;
  }>;
  
  // Latest meal plan info
  latest_meal_plan?: MealPlanVersion;
  
  created_at: string;
  updated_at: string;
}

export interface NutritionistDashboard {
  nutritionist: Nutritionist;
  stats: {
    total_patients: number;
    pending_invitations: number;
    pending_reviews: number;
    total_meal_plans: number;
    active_meal_plans: number;
  };
  pending_invitations: Array<{
    id: number;
    email: string;
    first_name?: string;
    last_name?: string;
    token: string;
    expires_at: string;
    created_at: string;
  }>;
  pending_reviews: Array<{
    id: number;
    email: string;
    first_name?: string;
    last_name?: string;
    completed_at: string;
    patient: PatientWithMealPlans;
  }>;
  patients: PatientWithMealPlans[];
}

export interface MealPlanComparison {
  patient_id: number;
  patient_name: string;
  plan1: {
    id: number;
    version: number;
    plan_name: string;
    status: string;
    created_at: string;
    meals: MealPlanMeal[];
  };
  plan2: {
    id: number;
    version: number;
    plan_name: string;
    status: string;
    created_at: string;
    meals: MealPlanMeal[];
  };
  changes: Array<{
    day_of_week: string;
    meal_type: string;
    old_recipe_id?: number;
    new_recipe_id?: number;
    change_type: 'added' | 'removed' | 'modified';
  }>;
  total_changes: number;
}

export interface MealPlanVersionStats {
  patient_id: number;
  patient_name: string;
  total_versions: number;
  approved_versions: number;
  draft_versions: number;
  latest_version?: number;
  latest_status?: string;
  first_created: string;
  last_updated: string;
  versions_timeline: Array<{
    version: number;
    status: string;
    created_at: string;
    is_latest: boolean;
    meal_count: number;
  }>;
}

// Patient-facing meal plan data (only latest version)
export interface PatientMealPlanView {
  patient: {
    name: string;
    email?: string;
    conditions: string[];
    intolerances: string[];
    preferences: string[];
  };
  meal_plan: {
    id: number;
    plan_name: string;
    version: number;
    start_date: string;
    end_date: string;
    notes?: string;
    approved_at?: string;
    nutritionist: {
      name: string;
      specialization?: string;
    };
  };
  meals: Array<{
    day: string; // "Monday", "Tuesday", etc.
    day_of_week: string; // "monday", "tuesday", etc.
    meals: Array<{
      type: string; // "Breakfast", "Lunch", etc.
      recipe_name: string;
      recipe_id: number;
      servings: number;
      scheduled_time?: string;
      calories: number;
      protein: number;
      carbs: number;
      fat: number;
      preparation_time?: number;
      cooking_time?: number;
      difficulty?: string;
      ingredients: Array<{
        name: string;
        quantity: number;
        unit: string;
      }>;
      instructions?: string;
    }>;
  }>;
}

export interface PatientMealPlanSummary {
  patient_name: string;
  plan_name: string;
  version: number;
  start_date: string;
  end_date: string;
  total_meals: number;
  nutritionist: string;
  daily_averages: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  };
  weekly_totals: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  };
}

// API Request/Response types
export interface CreateMealPlanVersionRequest {
  base_plan_id?: number; // If creating from existing plan
  plan_data?: {
    plan_name: string;
    start_date: string;
    end_date: string;
    notes?: string;
    meals?: Array<{
      recipe_id: number;
      day_of_week: string;
      meal_type: string;
      scheduled_time?: string;
      servings: number;
    }>;
  };
}

export interface CreateVersionFromExistingRequest {
  updates?: {
    plan_name?: string;
    start_date?: string;
    end_date?: string;
    notes?: string;
    meals?: Array<{
      recipe_id: number;
      day_of_week: string;
      meal_type: string;
      scheduled_time?: string;
      servings: number;
    }>;
  };
}

export interface ApproveMealPlanRequest {
  approval_notes?: string;
}

export interface CompareMealPlansRequest {
  plan_id_1: number;
  plan_id_2: number;
}
