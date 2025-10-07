import { useState, useEffect } from 'react';
import {
  Nutritionist,
  NutritionistDashboard,
  MealPlanVersion,
  PatientWithMealPlans,
  MealPlanComparison,
  MealPlanVersionStats,
  CreateMealPlanVersionRequest,
  CreateVersionFromExistingRequest,
  ApproveMealPlanRequest,
  CompareMealPlansRequest
} from '@/types/business-rules';

const API_BASE = 'http://localhost:5001/api/nutritionist';

// Hook for nutritionist profile management
export function useNutritionistProfile() {
  const [profile, setProfile] = useState<Nutritionist | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Get auth token from Firebase (you'll need to implement this)
      const token = await getAuthToken();
      
      const response = await fetch(`${API_BASE}/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        setProfile(result.data.nutritionist);
      } else {
        setError(result.message);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch profile');
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async (profileData: Partial<Nutritionist>) => {
    setLoading(true);
    setError(null);
    
    try {
      const token = await getAuthToken();
      
      const response = await fetch(`${API_BASE}/profile`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileData)
      });
      
      const result = await response.json();
      
      if (result.success) {
        setProfile(result.data.nutritionist);
        return { success: true };
      } else {
        setError(result.message);
        return { success: false, error: result.message };
      }
    } catch (err: any) {
      const error = err.message || 'Failed to update profile';
      setError(error);
      return { success: false, error };
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  return {
    profile,
    loading,
    error,
    updateProfile,
    refetch: fetchProfile
  };
}

// Hook for nutritionist dashboard
export function useNutritionistDashboard() {
  const [dashboardData, setDashboardData] = useState<NutritionistDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const token = await getAuthToken();
      
      const response = await fetch(`${API_BASE}/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        setDashboardData(result.data);
      } else {
        setError(result.message);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  return {
    dashboardData,
    loading,
    error,
    refetch: fetchDashboard
  };
}

// Hook for patient meal plan history (nutritionist view)
export function usePatientMealPlanHistory(patientId: number) {
  const [mealPlans, setMealPlans] = useState<MealPlanVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMealPlanHistory = async () => {
    if (!patientId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const token = await getAuthToken();
      
      const response = await fetch(`${API_BASE}/patients/${patientId}/meal-plans`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        setMealPlans(result.data.meal_plans);
      } else {
        setError(result.message);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch meal plan history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMealPlanHistory();
  }, [patientId]);

  return {
    mealPlans,
    loading,
    error,
    refetch: fetchMealPlanHistory
  };
}

// Hook for meal plan versioning operations
export function useMealPlanVersioning() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createMealPlanVersion = async (patientId: number, request: CreateMealPlanVersionRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      const token = await getAuthToken();
      
      const response = await fetch(`${API_BASE}/patients/${patientId}/meal-plans`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      });
      
      const result = await response.json();
      
      if (result.success) {
        return { success: true, data: result.data.meal_plan };
      } else {
        setError(result.message);
        return { success: false, error: result.message };
      }
    } catch (err: any) {
      const error = err.message || 'Failed to create meal plan version';
      setError(error);
      return { success: false, error };
    } finally {
      setLoading(false);
    }
  };

  const approveMealPlan = async (planId: number, request: ApproveMealPlanRequest = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const token = await getAuthToken();
      
      const response = await fetch(`${API_BASE}/meal-plans/${planId}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      });
      
      const result = await response.json();
      
      if (result.success) {
        return { success: true, data: result.data.meal_plan };
      } else {
        setError(result.message);
        return { success: false, error: result.message };
      }
    } catch (err: any) {
      const error = err.message || 'Failed to approve meal plan';
      setError(error);
      return { success: false, error };
    } finally {
      setLoading(false);
    }
  };

  const createVersionFromExisting = async (planId: number, request: CreateVersionFromExistingRequest = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const token = await getAuthToken();
      
      const response = await fetch(`${API_BASE}/meal-plans/${planId}/versions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      });
      
      const result = await response.json();
      
      if (result.success) {
        return { success: true, data: result.data.meal_plan };
      } else {
        setError(result.message);
        return { success: false, error: result.message };
      }
    } catch (err: any) {
      const error = err.message || 'Failed to create version from existing';
      setError(error);
      return { success: false, error };
    } finally {
      setLoading(false);
    }
  };

  const compareMealPlans = async (request: CompareMealPlansRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      const token = await getAuthToken();
      
      const response = await fetch(`${API_BASE}/meal-plans/compare`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      });
      
      const result = await response.json();
      
      if (result.success) {
        return { success: true, data: result.data as MealPlanComparison };
      } else {
        setError(result.message);
        return { success: false, error: result.message };
      }
    } catch (err: any) {
      const error = err.message || 'Failed to compare meal plans';
      setError(error);
      return { success: false, error };
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    createMealPlanVersion,
    approveMealPlan,
    createVersionFromExisting,
    compareMealPlans
  };
}

// Hook for meal plan version statistics
export function useMealPlanVersionStats(patientId: number) {
  const [stats, setStats] = useState<MealPlanVersionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    if (!patientId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const token = await getAuthToken();
      
      const response = await fetch(`${API_BASE}/patients/${patientId}/meal-plans/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        setStats(result.data);
      } else {
        setError(result.message);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch version statistics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [patientId]);

  return {
    stats,
    loading,
    error,
    refetch: fetchStats
  };
}

// Helper function to get auth token (implement based on your auth system)
async function getAuthToken(): Promise<string> {
  // This should return the Firebase auth token
  // You'll need to implement this based on your auth setup
  // For now, returning a placeholder
  return 'your-auth-token';
}
