import { useState, useEffect } from 'react';
import { useApi } from './useApi';
import { apiClient } from '@/lib/firebase/api';

// Medical Conditions
export interface MedicalCondition {
  id: string;
  condition_name: string;
  description?: string;
  severity_level: 'low' | 'medium' | 'high' | 'critical';
  is_active: boolean;
  created_at: string;
}

export function useMedicalConditions() {
  const [data, setData] = useState<{ medical_conditions: MedicalCondition[]; total: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/catalogs/medical-conditions');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const result = await response.json();
      setData({ medical_conditions: result, total: result.length });
    } catch (err: any) {
      setError(err.message || 'Failed to fetch medical conditions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { data, loading, error, refetch: fetchData };
}

export function useCreateMedicalCondition() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createCondition = async (data: {
    condition_name: string;
    description?: string;
    severity_level?: 'low' | 'medium' | 'high' | 'critical';
  }) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.post<{ medical_condition: MedicalCondition }>('/api/catalogs/medical-conditions', data as unknown as Record<string, unknown>);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to create medical condition');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createCondition, loading, error };
}

// Food Intolerances
export interface FoodIntolerance {
  id: string;
  intolerance_name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
}

export function useFoodIntolerances() {
  const [data, setData] = useState<{ food_intolerances: FoodIntolerance[]; total: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/catalogs/food-intolerances');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const result = await response.json();
      setData({ food_intolerances: result, total: result.length });
    } catch (err: any) {
      setError(err.message || 'Failed to fetch food intolerances');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { data, loading, error, refetch: fetchData };
}

export function useCreateFoodIntolerance() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createIntolerance = async (data: {
    intolerance_name: string;
    description?: string;
  }) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.post<{ food_intolerance: FoodIntolerance }>('/api/catalogs/food-intolerances', data as unknown as Record<string, unknown>);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to create food intolerance');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createIntolerance, loading, error };
}

// Dietary Preferences
export interface DietaryPreference {
  id: string;
  preference_name: string;
  description?: string;
  is_active: boolean;
  created_at: string;
}

export function useDietaryPreferences() {
  const [data, setData] = useState<{ dietary_preferences: DietaryPreference[]; total: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/catalogs/dietary-preferences');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const result = await response.json();
      setData({ dietary_preferences: result, total: result.length });
    } catch (err: any) {
      setError(err.message || 'Failed to fetch dietary preferences');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { data, loading, error, refetch: fetchData };
}

export function useCreateDietaryPreference() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createPreference = async (data: {
    preference_name: string;
    description?: string;
  }) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.post<{ dietary_preference: DietaryPreference }>('/api/catalogs/dietary-preferences', data as unknown as Record<string, unknown>);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to create dietary preference');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createPreference, loading, error };
}

// Ingredients
export interface Ingredient {
  id: string;
  ingredient_name: string;
  category?: string;
  calories_per_100g?: number;
  protein_per_100g?: number;
  carbs_per_100g?: number;
  fat_per_100g?: number;
  fiber_per_100g?: number;
  is_active: boolean;
  created_at: string;
}

export function useIngredients(search?: string) {
  const [data, setData] = useState<{ ingredients: Ingredient[]; total: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const url = search ? `http://localhost:8000/catalogs/ingredients?search=${encodeURIComponent(search)}` : 'http://localhost:8000/catalogs/ingredients';
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const result = await response.json();
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch ingredients');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [search]);

  return { data, loading, error, refetch: fetchData };
}

export function useCreateIngredient() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createIngredient = async (data: {
    ingredient_name: string;
    category?: string;
    calories_per_100g?: number;
    protein_per_100g?: number;
    carbs_per_100g?: number;
    fat_per_100g?: number;
    fiber_per_100g?: number;
  }) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.post<{ ingredient: Ingredient }>('/api/catalogs/ingredients', data as unknown as Record<string, unknown>);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to create ingredient');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createIngredient, loading, error };
}

// Recipe Tags
export interface RecipeTag {
  id: string;
  tag_name: string;
  color: string;
  is_active: boolean;
  created_at: string;
}

export function useRecipeTags() {
  const [data, setData] = useState<{ recipe_tags: RecipeTag[]; total: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/catalogs/recipe-tags');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      const result = await response.json();
      setData({ recipe_tags: result, total: result.length });
    } catch (err: any) {
      setError(err.message || 'Failed to fetch recipe tags');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return { data, loading, error, refetch: fetchData };
}

export function useCreateRecipeTag() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createTag = async (data: {
    tag_name: string;
    color?: string;
  }) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.post<{ recipe_tag: RecipeTag }>('/api/catalogs/recipe-tags', data as unknown as Record<string, unknown>);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to create recipe tag');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createTag, loading, error };
}

// Generic update and delete hooks
export function useUpdateCatalogItem() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateItem = async (catalogType: string, itemId: string, data: Record<string, any>) => {
    setLoading(true);
    setError(null);

    try {
      await apiClient.put(`/api/catalogs/${catalogType}/${itemId}`, data);
      return true;
    } catch (err: any) {
      setError(err.message || 'Failed to update item');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { updateItem, loading, error };
}

export function useDeleteCatalogItem() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const deleteItem = async (catalogType: string, itemId: string) => {
    setLoading(true);
    setError(null);

    try {
      // Mock delete functionality for now
      console.log(`Deleted ${catalogType} item with ID: ${itemId}`);
      return true;
    } catch (err: any) {
      setError(err.message || 'Failed to delete item');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { deleteItem, loading, error };
}
