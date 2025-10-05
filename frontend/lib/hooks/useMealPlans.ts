import { useState, useEffect } from 'react';

export interface MealPlan {
  id: string;
  plan_name: string;
  description?: string;
  patient_id?: string;
  patient_name?: string;
  start_date: string;
  end_date: string;
  status: 'draft' | 'active' | 'completed';
  target_calories?: number;
  target_protein?: number;
  target_carbs?: number;
  target_fat?: number;
  notes?: string;
  total_recipes?: number;
  is_active: boolean;
  created_by_uid?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateMealPlanData {
  plan_name: string;
  description?: string;
  patient_id?: string;
  start_date: string;
  end_date: string;
  status: 'draft' | 'active' | 'completed';
  target_calories?: number;
  target_protein?: number;
  target_carbs?: number;
  target_fat?: number;
  notes?: string;
}

// Get all meal plans (updated to use direct fetch)
export function useMealPlans(filters?: {
  patient_id?: string;
  status?: string;
  search?: string;
  start_date?: string;
  end_date?: string;
}) {
  const [data, setData] = useState<{ meal_plans: MealPlan[]; total: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMealPlans = async () => {
    setLoading(true);
    setError(null);
    
    try {
      let endpoint = 'http://localhost:8000/api/meal-plans';
      
      if (filters) {
        const params = new URLSearchParams();
        if (filters.patient_id) params.append('patient_id', filters.patient_id);
        if (filters.status) params.append('status', filters.status);
        if (filters.search) params.append('search', filters.search);
        if (filters.start_date) params.append('start_date', filters.start_date);
        if (filters.end_date) params.append('end_date', filters.end_date);
        
        if (params.toString()) {
          endpoint += `?${params.toString()}`;
        }
      }
      
      const response = await fetch(endpoint);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch meal plans');
      console.error('Error fetching meal plans:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMealPlans();
  }, [filters?.patient_id, filters?.status, filters?.search, filters?.start_date, filters?.end_date]);

  return {
    data,
    loading,
    error,
    refetch: fetchMealPlans
  };
}

// Get single meal plan (updated to use direct fetch)
export function useMealPlan(mealPlanId: string) {
  const [data, setData] = useState<{ meal_plan: MealPlan } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMealPlan = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:8000/api/meal-plans/${mealPlanId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch meal plan');
      console.error('Error fetching meal plan:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (mealPlanId) {
      fetchMealPlan();
    }
  }, [mealPlanId]);

  return {
    data,
    loading,
    error,
    refetch: fetchMealPlan
  };
}

// Create meal plan mutation (mock implementation for testing)
export function useCreateMealPlan() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createMealPlan = async (data: CreateMealPlanData) => {
    setLoading(true);
    setError(null);

    try {
      // Mock implementation - simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockMealPlan: MealPlan = {
        id: `meal_plan_${Date.now()}`,
        plan_name: data.plan_name,
        description: data.description,
        patient_id: data.patient_id,
        patient_name: data.patient_id === '1' ? 'John Doe' : data.patient_id === '2' ? 'Jane Smith' : data.patient_id === '3' ? 'Michael Johnson' : undefined,
        start_date: data.start_date,
        end_date: data.end_date,
        status: data.status,
        target_calories: data.target_calories,
        target_protein: data.target_protein,
        target_carbs: data.target_carbs,
        target_fat: data.target_fat,
        notes: data.notes,
        total_recipes: 0,
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      console.log('Mock meal plan created:', mockMealPlan);
      return { meal_plan: mockMealPlan };
    } catch (err: any) {
      setError(err.message || 'Failed to create meal plan');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createMealPlan, loading, error };
}

// Update meal plan mutation (mock implementation for testing)
export function useUpdateMealPlan() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateMealPlan = async (mealPlanId: string, data: Partial<CreateMealPlanData>) => {
    setLoading(true);
    setError(null);

    try {
      // Mock implementation - simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      console.log('Mock meal plan updated:', { mealPlanId, data });
      return { meal_plan: { id: mealPlanId, ...data } as MealPlan };
    } catch (err: any) {
      setError(err.message || 'Failed to update meal plan');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { updateMealPlan, loading, error };
}

// Delete meal plan mutation (mock implementation for testing)
export function useDeleteMealPlan() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const deleteMealPlan = async (mealPlanId: string) => {
    setLoading(true);
    setError(null);

    try {
      // Mock implementation - simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      console.log('Mock meal plan deleted:', mealPlanId);
      return true;
    } catch (err: any) {
      setError(err.message || 'Failed to delete meal plan');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { deleteMealPlan, loading, error };
}

// Generate meal plan from patient restrictions (mock implementation)
export function useGenerateMealPlan() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateMealPlan = async (patientId: string, days: number, preferences?: any) => {
    setLoading(true);
    setError(null);

    try {
      // Mock implementation - simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockGeneratedPlan: MealPlan = {
        id: `generated_plan_${Date.now()}`,
        plan_name: `AI Generated Plan - ${days} Days`,
        description: `Automatically generated meal plan based on patient restrictions and preferences`,
        patient_id: patientId,
        patient_name: patientId === '1' ? 'John Doe' : patientId === '2' ? 'Jane Smith' : 'Michael Johnson',
        start_date: new Date().toISOString().split('T')[0],
        end_date: new Date(Date.now() + days * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        status: 'draft',
        target_calories: 2000,
        target_protein: 150,
        target_carbs: 250,
        target_fat: 70,
        notes: 'AI generated based on patient dietary restrictions and preferences',
        total_recipes: days * 3, // 3 meals per day
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      console.log('Mock meal plan generated:', mockGeneratedPlan);
      return { meal_plan: mockGeneratedPlan };
    } catch (err: any) {
      setError(err.message || 'Failed to generate meal plan');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { generateMealPlan, loading, error };
}
