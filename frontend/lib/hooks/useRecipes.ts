import { useState, useEffect } from 'react';
import { useApi } from './useApi';
import { apiClient } from '@/lib/firebase/api';

export interface Recipe {
  id: string;
  recipe_name: string;
  description?: string;
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  preparation_time?: number;
  cooking_time?: number;
  servings: number;
  difficulty_level?: 'easy' | 'medium' | 'hard';
  total_calories?: number;
  total_protein?: number;
  total_carbs?: number;
  total_fat?: number;
  total_fiber?: number;
  instructions?: string;
  image_url?: string;
  is_active: boolean;
  created_by_uid?: string;
  created_at: string;
  updated_at: string;
  ingredients?: RecipeIngredient[];
  tags?: string[];
}

export interface RecipeIngredient {
  id?: string;
  ingredient_id: string;
  ingredient_name: string;
  quantity: number;
  unit: string;
  calories_per_100g?: number;
  protein_per_100g?: number;
  carbs_per_100g?: number;
  fat_per_100g?: number;
  fiber_per_100g?: number;
}

export interface CreateRecipeData {
  recipe_name: string;
  description?: string;
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  preparation_time?: number;
  cooking_time?: number;
  servings: number;
  difficulty_level?: 'easy' | 'medium' | 'hard';
  instructions?: string;
  image_url?: string;
  ingredients: RecipeIngredient[];
  tags?: string[];
}

// Get all recipes (updated to use direct fetch)
export function useRecipes(filters?: {
  meal_type?: string;
  is_active?: boolean;
  search?: string;
  created_by?: string;
}) {
  const [data, setData] = useState<{ recipes: Recipe[]; total: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRecipes = async () => {
    setLoading(true);
    setError(null);
    
    try {
      let endpoint = 'http://localhost:8000/api/recipes';
      
      if (filters) {
        const params = new URLSearchParams();
        if (filters.meal_type) params.append('meal_type', filters.meal_type);
        if (filters.is_active !== undefined) params.append('is_active', filters.is_active.toString());
        if (filters.search) params.append('search', filters.search);
        if (filters.created_by) params.append('created_by', filters.created_by);
        
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
      setError(err.message || 'Failed to fetch recipes');
      console.error('Error fetching recipes:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecipes();
  }, [filters?.meal_type, filters?.is_active, filters?.search, filters?.created_by]);

  return {
    data,
    loading,
    error,
    refetch: fetchRecipes
  };
}

// Get single recipe (updated to use direct fetch)
export function useRecipe(recipeId: string) {
  const [data, setData] = useState<{ recipe: Recipe } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRecipe = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:8000/api/recipes/${recipeId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch recipe');
      console.error('Error fetching recipe:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (recipeId) {
      fetchRecipe();
    }
  }, [recipeId]);

  return {
    data,
    loading,
    error,
    refetch: fetchRecipe
  };
}

// Get compatible recipes for patient (updated to use direct fetch)
export function useCompatibleRecipes(patientId: string) {
  const [data, setData] = useState<{
    compatible_recipes: Recipe[];
    by_meal_type: {
      breakfast: Recipe[];
      lunch: Recipe[];
      dinner: Recipe[];
      snack: Recipe[];
    };
    total: number;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCompatibleRecipes = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:8000/api/recipes/compatible/${patientId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch compatible recipes');
      console.error('Error fetching compatible recipes:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (patientId) {
      fetchCompatibleRecipes();
    }
  }, [patientId]);

  return {
    data,
    loading,
    error,
    refetch: fetchCompatibleRecipes
  };
}

// Create recipe mutation (mock implementation for testing)
export function useCreateRecipe() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createRecipe = async (data: CreateRecipeData) => {
    setLoading(true);
    setError(null);

    try {
      // Mock implementation - simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockRecipe: Recipe = {
        id: `recipe_${Date.now()}`,
        recipe_name: data.recipe_name,
        description: data.description,
        meal_type: data.meal_type,
        preparation_time: data.preparation_time,
        cooking_time: data.cooking_time,
        servings: data.servings,
        difficulty_level: data.difficulty_level,
        instructions: data.instructions,
        image_url: data.image_url,
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        ingredients: data.ingredients,
        tags: data.tags,
        total_calories: 250,
        total_protein: 15,
        total_carbs: 20,
        total_fat: 8,
        total_fiber: 3
      };
      
      console.log('Mock recipe created:', mockRecipe);
      return { recipe: mockRecipe };
    } catch (err: any) {
      setError(err.message || 'Failed to create recipe');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createRecipe, loading, error };
}

// Update recipe mutation (mock implementation for testing)
export function useUpdateRecipe() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateRecipe = async (recipeId: string, data: Partial<CreateRecipeData>) => {
    setLoading(true);
    setError(null);

    try {
      // Mock implementation - simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      console.log('Mock recipe updated:', { recipeId, data });
      return { recipe: { id: recipeId, ...data } as Recipe };
    } catch (err: any) {
      setError(err.message || 'Failed to update recipe');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { updateRecipe, loading, error };
}

// Delete recipe mutation (mock implementation for testing)
export function useDeleteRecipe() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const deleteRecipe = async (recipeId: string) => {
    setLoading(true);
    setError(null);

    try {
      // Mock implementation - simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      console.log('Mock recipe deleted:', recipeId);
      return true;
    } catch (err: any) {
      setError(err.message || 'Failed to delete recipe');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { deleteRecipe, loading, error };
}

// Duplicate recipe mutation (mock implementation for testing)
export function useDuplicateRecipe() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const duplicateRecipe = async (recipeId: string) => {
    setLoading(true);
    setError(null);

    try {
      // Mock implementation - simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockDuplicatedRecipe: Recipe = {
        id: `recipe_duplicate_${Date.now()}`,
        recipe_name: 'Copy of Recipe',
        description: 'Duplicated recipe',
        meal_type: 'lunch',
        servings: 1,
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        total_calories: 200,
        total_protein: 10,
        total_carbs: 15,
        total_fat: 5,
        total_fiber: 2
      };
      
      console.log('Mock recipe duplicated:', { originalId: recipeId, newRecipe: mockDuplicatedRecipe });
      return { recipe: mockDuplicatedRecipe };
    } catch (err: any) {
      setError(err.message || 'Failed to duplicate recipe');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { duplicateRecipe, loading, error };
}

// Create batch recipes mutation (mock implementation for testing)
export function useCreateBatchRecipes() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createBatchRecipes = async (recipes: CreateRecipeData[]) => {
    setLoading(true);
    setError(null);

    try {
      // Mock implementation - simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockCreatedRecipes: Recipe[] = recipes.map((recipe, index) => ({
        id: `batch_recipe_${Date.now()}_${index}`,
        recipe_name: recipe.recipe_name,
        description: recipe.description,
        meal_type: recipe.meal_type,
        servings: recipe.servings,
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        total_calories: 200 + index * 50,
        total_protein: 10 + index * 5,
        total_carbs: 15 + index * 3,
        total_fat: 5 + index * 2,
        total_fiber: 2 + index
      }));
      
      console.log('Mock batch recipes created:', mockCreatedRecipes);
      return {
        created_recipes: mockCreatedRecipes,
        created_count: mockCreatedRecipes.length,
        errors: []
      };
    } catch (err: any) {
      setError(err.message || 'Failed to create batch recipes');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createBatchRecipes, loading, error };
}
