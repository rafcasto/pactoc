import React from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { NutritionBadge } from '@/components/ui/NutritionBadge';
import { Clock, Users, ChefHat, Eye, Edit, Copy, Trash2 } from 'lucide-react';
import { Recipe } from '@/lib/hooks/useRecipes';

interface RecipeCardProps {
  recipe: Recipe;
  onView?: (recipe: Recipe) => void;
  onEdit?: (recipe: Recipe) => void;
  onDuplicate?: (recipe: Recipe) => void;
  onDelete?: (recipe: Recipe) => void;
  className?: string;
}

export function RecipeCard({ 
  recipe, 
  onView, 
  onEdit, 
  onDuplicate, 
  onDelete,
  className 
}: RecipeCardProps) {
  const getMealTypeColor = (mealType: string) => {
    switch (mealType) {
      case 'breakfast':
        return 'bg-yellow-100 text-yellow-800';
      case 'lunch':
        return 'bg-blue-100 text-blue-800';
      case 'dinner':
        return 'bg-purple-100 text-purple-800';
      case 'snack':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyColor = (difficulty?: string) => {
    switch (difficulty) {
      case 'easy':
        return 'text-green-600';
      case 'medium':
        return 'text-yellow-600';
      case 'hard':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const totalTime = (recipe.preparation_time || 0) + (recipe.cooking_time || 0);

  return (
    <Card className={`overflow-hidden hover:shadow-lg transition-shadow ${className}`}>
      {/* Image */}
      <div className="h-48 bg-gray-200 relative overflow-hidden">
        {recipe.image_url ? (
          <img
            src={recipe.image_url}
            alt={recipe.recipe_name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <ChefHat className="w-16 h-16 text-gray-400" />
          </div>
        )}
        
        {/* Meal Type Badge */}
        <div className="absolute top-2 left-2">
          <span className={`px-2 py-1 text-xs font-medium rounded-full capitalize ${getMealTypeColor(recipe.meal_type)}`}>
            {recipe.meal_type}
          </span>
        </div>
        
        {/* Actions */}
        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <div className="flex space-x-1">
            {onView && (
              <Button
                size="sm"
                variant="ghost"
                className="bg-white/80 hover:bg-white"
                onClick={(e) => {
                  e.stopPropagation();
                  onView(recipe);
                }}
              >
                <Eye className="w-4 h-4" />
              </Button>
            )}
            {onEdit && (
              <Button
                size="sm"
                variant="ghost"
                className="bg-white/80 hover:bg-white"
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(recipe);
                }}
              >
                <Edit className="w-4 h-4" />
              </Button>
            )}
            {onDuplicate && (
              <Button
                size="sm"
                variant="ghost"
                className="bg-white/80 hover:bg-white"
                onClick={(e) => {
                  e.stopPropagation();
                  onDuplicate(recipe);
                }}
              >
                <Copy className="w-4 h-4" />
              </Button>
            )}
            {onDelete && (
              <Button
                size="sm"
                variant="ghost"
                className="bg-white/80 hover:bg-white text-red-600"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(recipe);
                }}
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Title */}
        <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
          {recipe.recipe_name}
        </h3>

        {/* Description */}
        {recipe.description && (
          <p className="text-sm text-gray-600 mb-3 line-clamp-2">
            {recipe.description}
          </p>
        )}

        {/* Recipe Info */}
        <div className="flex items-center justify-between mb-3 text-sm text-gray-500">
          <div className="flex items-center space-x-4">
            {totalTime > 0 && (
              <div className="flex items-center">
                <Clock className="w-4 h-4 mr-1" />
                <span>{totalTime}min</span>
              </div>
            )}
            <div className="flex items-center">
              <Users className="w-4 h-4 mr-1" />
              <span>{recipe.servings} serving{recipe.servings !== 1 ? 's' : ''}</span>
            </div>
            {recipe.difficulty_level && (
              <div className={`font-medium capitalize ${getDifficultyColor(recipe.difficulty_level)}`}>
                {recipe.difficulty_level}
              </div>
            )}
          </div>
        </div>

        {/* Nutrition Info */}
        <NutritionBadge
          nutrition={{
            total_calories: recipe.total_calories,
            total_protein: recipe.total_protein,
            total_carbs: recipe.total_carbs,
            total_fat: recipe.total_fat,
            total_fiber: recipe.total_fiber
          }}
          size="sm"
          className="mb-3"
        />

        {/* Tags */}
        {recipe.tags && recipe.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {recipe.tags.slice(0, 3).map((tag, index) => (
              <span
                key={index}
                className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full"
              >
                {tag}
              </span>
            ))}
            {recipe.tags.length > 3 && (
              <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full">
                +{recipe.tags.length - 3} more
              </span>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>
            Created {new Date(recipe.created_at).toLocaleDateString()}
          </span>
          {recipe.ingredients && (
            <span>
              {recipe.ingredients.length} ingredient{recipe.ingredients.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>
    </Card>
  );
}

interface RecipeGridProps {
  recipes: Recipe[];
  loading?: boolean;
  onView?: (recipe: Recipe) => void;
  onEdit?: (recipe: Recipe) => void;
  onDuplicate?: (recipe: Recipe) => void;
  onDelete?: (recipe: Recipe) => void;
  emptyMessage?: string;
  className?: string;
}

export function RecipeGrid({
  recipes,
  loading = false,
  onView,
  onEdit,
  onDuplicate,
  onDelete,
  emptyMessage = "No recipes found",
  className
}: RecipeGridProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {Array.from({ length: 8 }).map((_, index) => (
          <Card key={index} className="overflow-hidden animate-pulse">
            <div className="h-48 bg-gray-200"></div>
            <div className="p-4 space-y-3">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-3 bg-gray-200 rounded w-3/4"></div>
              <div className="flex space-x-2">
                <div className="h-6 bg-gray-200 rounded w-16"></div>
                <div className="h-6 bg-gray-200 rounded w-20"></div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    );
  }

  if (recipes.length === 0) {
    return (
      <div className="text-center py-12">
        <ChefHat className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Recipes</h3>
        <p className="text-gray-500">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 ${className}`}>
      {recipes.map((recipe) => (
        <div key={recipe.id} className="group">
          <RecipeCard
            recipe={recipe}
            onView={onView}
            onEdit={onEdit}
            onDuplicate={onDuplicate}
            onDelete={onDelete}
          />
        </div>
      ))}
    </div>
  );
}
