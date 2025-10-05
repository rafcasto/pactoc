'use client';

import React, { useState } from 'react';
import { AuthenticatedLayout } from '@/components/layout/AuthenticatedLayout';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Modal, ModalFooter } from '@/components/ui/Modal';
import { RecipeGrid } from '@/components/recipe/RecipeCard';
import { NutritionBadge, DetailedNutrition } from '@/components/ui/NutritionBadge';
import { useRecipes, useCreateRecipe, useUpdateRecipe, useDeleteRecipe, useDuplicateRecipe, type Recipe, type CreateRecipeData } from '@/lib/hooks/useRecipes';
import { Plus, Search, Filter, ChefHat, Clock, Users, AlertCircle } from 'lucide-react';

export default function RecipesPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMealType, setSelectedMealType] = useState<string>('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);

  // Hooks
  const { data: recipesData, loading, error, refetch } = useRecipes({
    search: searchTerm || undefined,
    meal_type: selectedMealType || undefined
  });
  const { createRecipe, loading: creating } = useCreateRecipe();
  const { updateRecipe, loading: updating } = useUpdateRecipe();
  const { deleteRecipe, loading: deleting } = useDeleteRecipe();
  const { duplicateRecipe, loading: duplicating } = useDuplicateRecipe();

  const recipes = recipesData?.recipes || [];

  const handleCreateRecipe = async (data: CreateRecipeData | Partial<CreateRecipeData>) => {
    try {
      await createRecipe(data as CreateRecipeData);
      setShowCreateModal(false);
      refetch();
    } catch (error) {
      console.error('Failed to create recipe:', error);
    }
  };

  const handleUpdateRecipe = async (data: CreateRecipeData | Partial<CreateRecipeData>) => {
    if (!selectedRecipe) return;
    
    try {
      await updateRecipe(selectedRecipe.id, data);
      setShowEditModal(false);
      setSelectedRecipe(null);
      refetch();
    } catch (error) {
      console.error('Failed to update recipe:', error);
    }
  };

  const handleDeleteRecipe = async (recipe: Recipe) => {
    if (confirm(`Are you sure you want to delete "${recipe.recipe_name}"?`)) {
      try {
        await deleteRecipe(recipe.id);
        refetch();
      } catch (error) {
        console.error('Failed to delete recipe:', error);
      }
    }
  };

  const handleDuplicateRecipe = async (recipe: Recipe) => {
    try {
      await duplicateRecipe(recipe.id);
      refetch();
    } catch (error) {
      console.error('Failed to duplicate recipe:', error);
    }
  };

  const handleViewRecipe = (recipe: Recipe) => {
    setSelectedRecipe(recipe);
    setShowViewModal(true);
  };

  const handleEditRecipe = (recipe: Recipe) => {
    setSelectedRecipe(recipe);
    setShowEditModal(true);
  };

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading recipes</h3>
          <p className="text-gray-500 mb-4">{error}</p>
          <Button onClick={refetch}>Try Again</Button>
        </div>
      </div>
    );
  }

  return (
    <AuthenticatedLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Recipes</h1>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          New Recipe
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-2xl font-bold text-gray-900">{recipes.length}</div>
          <div className="text-sm text-gray-500">Total Recipes</div>
        </Card>
        <Card className="p-4">
          <div className="text-2xl font-bold text-yellow-600">
            {recipes.filter(r => r.meal_type === 'breakfast').length}
          </div>
          <div className="text-sm text-gray-500">Breakfast</div>
        </Card>
        <Card className="p-4">
          <div className="text-2xl font-bold text-blue-600">
            {recipes.filter(r => r.meal_type === 'lunch').length}
          </div>
          <div className="text-sm text-gray-500">Lunch</div>
        </Card>
        <Card className="p-4">
          <div className="text-2xl font-bold text-purple-600">
            {recipes.filter(r => r.meal_type === 'dinner').length}
          </div>
          <div className="text-sm text-gray-500">Dinner</div>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            type="text"
            placeholder="Search recipes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <select
          value={selectedMealType}
          onChange={(e) => setSelectedMealType(e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-2 text-sm"
        >
          <option value="">All Meal Types</option>
          <option value="breakfast">Breakfast</option>
          <option value="lunch">Lunch</option>
          <option value="dinner">Dinner</option>
          <option value="snack">Snack</option>
        </select>
      </div>

      {/* Recipes Grid */}
      <RecipeGrid
        recipes={recipes}
        loading={loading}
        onView={handleViewRecipe}
        onEdit={handleEditRecipe}
        onDuplicate={handleDuplicateRecipe}
        onDelete={handleDeleteRecipe}
        emptyMessage="No recipes found. Create your first recipe to get started!"
      />

      {/* Create Recipe Modal */}
      {showCreateModal && (
        <RecipeFormModal
          title="Create New Recipe"
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateRecipe}
          loading={creating}
        />
      )}

      {/* Edit Recipe Modal */}
      {showEditModal && selectedRecipe && (
        <RecipeFormModal
          title="Edit Recipe"
          recipe={selectedRecipe}
          onClose={() => {
            setShowEditModal(false);
            setSelectedRecipe(null);
          }}
          onSubmit={handleUpdateRecipe}
          loading={updating}
        />
      )}

      {/* View Recipe Modal */}
      {showViewModal && selectedRecipe && (
        <ViewRecipeModal
          recipe={selectedRecipe}
          onClose={() => {
            setShowViewModal(false);
            setSelectedRecipe(null);
          }}
          onEdit={() => {
            setShowViewModal(false);
            setShowEditModal(true);
          }}
        />
      )}
      </div>
    </AuthenticatedLayout>
  );
}

// Recipe Form Modal Component
interface RecipeFormModalProps {
  title: string;
  recipe?: Recipe;
  onClose: () => void;
  onSubmit: (data: CreateRecipeData | Partial<CreateRecipeData>) => void;
  loading: boolean;
}

function RecipeFormModal({ title, recipe, onClose, onSubmit, loading }: RecipeFormModalProps) {
  const [formData, setFormData] = useState({
    recipe_name: recipe?.recipe_name || '',
    description: recipe?.description || '',
    meal_type: recipe?.meal_type || 'lunch' as const,
    preparation_time: recipe?.preparation_time || 0,
    cooking_time: recipe?.cooking_time || 0,
    servings: recipe?.servings || 1,
    difficulty_level: recipe?.difficulty_level || 'easy' as const,
    instructions: recipe?.instructions || '',
    image_url: recipe?.image_url || '',
    ingredients: recipe?.ingredients || [] as any[],
    tags: recipe?.tags || []
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.recipe_name) return;

    onSubmit(formData);
  };

  return (
    <Modal
      open={true}
      onClose={onClose}
      title={title}
      size="xl"
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Recipe Name *
            </label>
            <Input
              type="text"
              value={formData.recipe_name}
              onChange={(e) => setFormData({ ...formData, recipe_name: e.target.value })}
              required
              placeholder="Enter recipe name..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Meal Type *
            </label>
            <select
              value={formData.meal_type}
              onChange={(e) => setFormData({ ...formData, meal_type: e.target.value as any })}
              required
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="breakfast">Breakfast</option>
              <option value="lunch">Lunch</option>
              <option value="dinner">Dinner</option>
              <option value="snack">Snack</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={3}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            placeholder="Brief description of the recipe..."
          />
        </div>

        {/* Time and Servings */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Prep Time (min)
            </label>
            <Input
              type="number"
              value={formData.preparation_time}
              onChange={(e) => setFormData({ ...formData, preparation_time: parseInt(e.target.value) || 0 })}
              min="0"
              placeholder="0"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Cook Time (min)
            </label>
            <Input
              type="number"
              value={formData.cooking_time}
              onChange={(e) => setFormData({ ...formData, cooking_time: parseInt(e.target.value) || 0 })}
              min="0"
              placeholder="0"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Servings
            </label>
            <Input
              type="number"
              value={formData.servings}
              onChange={(e) => setFormData({ ...formData, servings: parseInt(e.target.value) || 1 })}
              min="1"
              required
              placeholder="1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Difficulty
            </label>
            <select
              value={formData.difficulty_level}
              onChange={(e) => setFormData({ ...formData, difficulty_level: e.target.value as any })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
        </div>

        {/* Instructions */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Instructions
          </label>
          <textarea
            value={formData.instructions}
            onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
            rows={6}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            placeholder="Step-by-step cooking instructions..."
          />
        </div>

        {/* Image URL */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Image URL
          </label>
          <Input
            type="url"
            value={formData.image_url}
            onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
            placeholder="https://example.com/recipe-image.jpg"
          />
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={loading} disabled={!formData.recipe_name}>
            {recipe ? 'Update Recipe' : 'Create Recipe'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}

// View Recipe Modal Component
interface ViewRecipeModalProps {
  recipe: Recipe;
  onClose: () => void;
  onEdit: () => void;
}

function ViewRecipeModal({ recipe, onClose, onEdit }: ViewRecipeModalProps) {
  const totalTime = (recipe.preparation_time || 0) + (recipe.cooking_time || 0);

  return (
    <Modal
      open={true}
      onClose={onClose}
      title={recipe.recipe_name}
      size="xl"
    >
      <div className="space-y-6">
        {/* Recipe Image */}
        {recipe.image_url && (
          <div className="w-full h-64 rounded-lg overflow-hidden">
            <img
              src={recipe.image_url}
              alt={recipe.recipe_name}
              className="w-full h-full object-cover"
            />
          </div>
        )}

        {/* Recipe Info */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="flex items-center justify-center">
            <Clock className="w-5 h-5 text-gray-400 mr-2" />
            <span className="text-sm">{totalTime || 0} min</span>
          </div>
          <div className="flex items-center justify-center">
            <Users className="w-5 h-5 text-gray-400 mr-2" />
            <span className="text-sm">{recipe.servings} serving{recipe.servings !== 1 ? 's' : ''}</span>
          </div>
          <div className="flex items-center justify-center">
            <ChefHat className="w-5 h-5 text-gray-400 mr-2" />
            <span className="text-sm capitalize">{recipe.difficulty_level || 'Easy'}</span>
          </div>
          <div className="flex items-center justify-center">
            <span className={`px-3 py-1 text-xs font-medium rounded-full capitalize ${
              recipe.meal_type === 'breakfast' ? 'bg-yellow-100 text-yellow-800' :
              recipe.meal_type === 'lunch' ? 'bg-blue-100 text-blue-800' :
              recipe.meal_type === 'dinner' ? 'bg-purple-100 text-purple-800' :
              'bg-green-100 text-green-800'
            }`}>
              {recipe.meal_type}
            </span>
          </div>
        </div>

        {/* Description */}
        {recipe.description && (
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Description</h4>
            <p className="text-gray-600">{recipe.description}</p>
          </div>
        )}

        {/* Nutrition */}
        <div>
          <h4 className="font-medium text-gray-900 mb-3">Nutrition Information</h4>
          <DetailedNutrition
            nutrition={{
              total_calories: recipe.total_calories,
              total_protein: recipe.total_protein,
              total_carbs: recipe.total_carbs,
              total_fat: recipe.total_fat,
              total_fiber: recipe.total_fiber
            }}
            servings={recipe.servings}
          />
        </div>

        {/* Ingredients */}
        {recipe.ingredients && recipe.ingredients.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Ingredients</h4>
            <ul className="space-y-2">
              {recipe.ingredients.map((ingredient, index) => (
                <li key={index} className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="font-medium">{ingredient.ingredient_name}</span>
                  <span className="text-gray-600">{ingredient.quantity} {ingredient.unit}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Instructions */}
        {recipe.instructions && (
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Instructions</h4>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-gray-700 whitespace-pre-wrap">{recipe.instructions}</p>
            </div>
          </div>
        )}

        {/* Tags */}
        {recipe.tags && recipe.tags.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Tags</h4>
            <div className="flex flex-wrap gap-2">
              {recipe.tags.map((tag, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        <ModalFooter>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
          <Button onClick={onEdit}>
            Edit Recipe
          </Button>
        </ModalFooter>
      </div>
    </Modal>
  );
}
