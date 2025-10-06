'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { ArrowLeft, Clock, Users, Utensils, Info, Loader2, AlertCircle } from 'lucide-react';

// Get API base URL from environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Patient {
  first_name: string;
  conditions: string[];
  intolerances: string[];
}

interface Recipe {
  recipe_name: string;
  description?: string;
  calories: number;
  protein: number;
  carbs: number;
  fiber: number;
  preparation_time?: number;
  cooking_time?: number;
  difficulty_level?: string;
  tags: string[];
  ingredients: string[];
  instructions: string[];
  image_url?: string;
}

interface Meal {
  type: string;
  time: string;
  servings: number;
  recipe: Recipe;
}

interface DayMeals {
  day: string;
  day_of_week: string;
  meals: Meal[];
}

interface MealPlan {
  plan_id: number;
  plan_name: string;
  start_date: string;
  end_date: string;
  meals: DayMeals[];
}

interface PlanData {
  patient: Patient;
  meal_plan: MealPlan;
}

const MealCard: React.FC<{ meal: Meal }> = ({ meal }) => {
  const { recipe } = meal;
  
  const getMealIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'desayuno':
        return '🌅';
      case 'almuerzo':
        return '🌞';
      case 'cena':
        return '🌙';
      default:
        return '🍽️';
    }
  };

  const getDifficultyColor = (difficulty?: string) => {
    switch (difficulty) {
      case 'easy':
        return 'text-green-600 bg-green-50';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50';
      case 'hard':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getDifficultyText = (difficulty?: string) => {
    switch (difficulty) {
      case 'easy':
        return 'Fácil';
      case 'medium':
        return 'Intermedio';
      case 'hard':
        return 'Difícil';
      default:
        return 'N/A';
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{getMealIcon(meal.type)}</span>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-medium text-gray-900">{meal.type}</h3>
              {meal.time && (
                <div className="flex items-center text-sm text-gray-500 bg-gray-50 px-2 py-1 rounded-md">
                  <Clock className="w-3 h-3 mr-1" />
                  {meal.time}
                </div>
              )}
            </div>
            <h4 className="text-lg font-semibold text-gray-800 mt-1">{recipe.recipe_name}</h4>
          </div>
        </div>
      </div>

      {/* Nutrition Info */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        <div className="text-center p-2 bg-blue-50 rounded-lg">
          <div className="text-lg font-bold text-blue-600">{recipe.calories}</div>
          <div className="text-xs text-blue-600">Cal</div>
        </div>
        <div className="text-center p-2 bg-purple-50 rounded-lg">
          <div className="text-lg font-bold text-purple-600">{recipe.carbs}g</div>
          <div className="text-xs text-purple-600">Carb</div>
        </div>
        <div className="text-center p-2 bg-green-50 rounded-lg">
          <div className="text-lg font-bold text-green-600">{recipe.protein}g</div>
          <div className="text-xs text-green-600">Prot</div>
        </div>
        <div className="text-center p-2 bg-orange-50 rounded-lg">
          <div className="text-lg font-bold text-orange-600">{recipe.fiber}g</div>
          <div className="text-xs text-orange-600">Fibra</div>
        </div>
      </div>

      {/* Recipe Details */}
      <div className="space-y-4">
        {/* Tags */}
        {recipe.tags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {recipe.tags.map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
              >
                ✓ {tag}
              </span>
            ))}
          </div>
        )}

        {/* Time and Difficulty */}
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          {recipe.preparation_time && (
            <div className="flex items-center">
              <Clock className="w-4 h-4 mr-1" />
              Prep: {recipe.preparation_time} min
            </div>
          )}
          {recipe.cooking_time && (
            <div className="flex items-center">
              <Utensils className="w-4 h-4 mr-1" />
              Cocción: {recipe.cooking_time} min
            </div>
          )}
          {recipe.difficulty_level && (
            <span className={`px-2 py-1 rounded-md text-xs font-medium ${getDifficultyColor(recipe.difficulty_level)}`}>
              {getDifficultyText(recipe.difficulty_level)}
            </span>
          )}
        </div>

        {/* Ingredients and Instructions in two columns on desktop */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Ingredients */}
          <div>
            <h5 className="font-medium text-gray-900 mb-2">Ingredientes</h5>
            <ul className="space-y-1 text-sm text-gray-700">
              {recipe.ingredients.map((ingredient, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  <span>{ingredient}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Instructions */}
          <div>
            <h5 className="font-medium text-gray-900 mb-2">Instrucciones</h5>
            <ol className="space-y-2 text-sm text-gray-700">
              {recipe.instructions.map((instruction, index) => (
                <li key={index} className="flex items-start">
                  <span className="flex-shrink-0 w-5 h-5 bg-blue-100 text-blue-600 rounded-full text-xs font-medium flex items-center justify-center mr-2 mt-0.5">
                    {index + 1}
                  </span>
                  <span>{instruction.replace(/^\d+\.\s*/, '')}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
};

export default function ViewMealPlan() {
  const { token } = useParams();
  const [planData, setPlanData] = useState<PlanData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      fetchPlan();
    }
  }, [token]);

  const fetchPlan = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/public/meal-plans/${token}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Plan no encontrado');
      }
      
      const data = await response.json();
      setPlanData(data);
    } catch (error) {
      console.error('Error fetching plan:', error);
      setError(error instanceof Error ? error.message : 'Error cargando el plan');
    } finally {
      setLoading(false);
    }
  };

  const formatDateRange = (startDate: string, endDate: string) => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    const options: Intl.DateTimeFormatOptions = { 
      day: 'numeric', 
      month: 'short'
    };
    
    return `${start.toLocaleDateString('es-ES', options)} - ${end.toLocaleDateString('es-ES', options)}, ${end.getFullYear()}`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Cargando tu plan de comidas...</p>
        </div>
      </div>
    );
  }

  if (error || !planData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-light text-gray-900 mb-2">Plan No Encontrado</h1>
          <p className="text-gray-600 mb-4">
            {error || 'No se pudo cargar tu plan de comidas.'}
          </p>
          <p className="text-sm text-gray-500">
            Verifica el link o contacta con tu nutricionista.
          </p>
        </div>
      </div>
    );
  }

  const { patient, meal_plan } = planData;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <button 
            onClick={() => window.history.back()}
            className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Volver
          </button>
          
          <div className="bg-white rounded-2xl shadow-sm p-6">
            <h1 className="text-3xl font-light text-gray-900 mb-2">
              Tu Plan de Comidas Personalizado
            </h1>
            <p className="text-gray-600 mb-4">
              Semana del {formatDateRange(meal_plan.start_date, meal_plan.end_date)}
            </p>
            
            {/* Patient Info */}
            <div className="bg-blue-50 rounded-xl p-4">
              <div className="flex items-start space-x-2">
                <Info className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-blue-900 mb-1">
                    Personalizado para: {patient.first_name}
                  </p>
                  <div className="text-sm text-blue-700 space-y-1">
                    {patient.conditions.length > 0 && (
                      <p>
                        <span className="font-medium">Condiciones:</span> {patient.conditions.join(', ')}
                      </p>
                    )}
                    {patient.intolerances.length > 0 && (
                      <p>
                        <span className="font-medium">Intolerancias:</span> {patient.intolerances.join(', ')}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Meal Plan Days */}
        <div className="space-y-8">
          {meal_plan.meals.map((dayMeals, dayIndex) => (
            <div key={dayIndex} className="bg-white rounded-2xl shadow-sm overflow-hidden">
              {/* Day Header */}
              <div className="bg-gray-50 px-6 py-4 border-b border-gray-100">
                <h2 className="text-xl font-semibold text-gray-900">{dayMeals.day}</h2>
              </div>
              
              {/* Meals */}
              <div className="p-6">
                <div className="grid grid-cols-1 lg:grid-cols-1 gap-6">
                  {dayMeals.meals.map((meal, mealIndex) => (
                    <MealCard key={mealIndex} meal={meal} />
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="mt-12 text-center py-8">
          <p className="text-gray-500 text-sm">
            Este plan ha sido personalizado específicamente para ti. 
            Para dudas o cambios, contacta con tu nutricionista.
          </p>
        </div>
      </div>
    </div>
  );
}
