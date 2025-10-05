'use client';

import React, { useState } from 'react';
import { AuthenticatedLayout } from '@/components/layout/AuthenticatedLayout';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { DataTable } from '@/components/ui/DataTable';
import { Modal, ModalFooter } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { 
  useMedicalConditions, 
  useCreateMedicalCondition,
  useFoodIntolerances,
  useCreateFoodIntolerance,
  useDietaryPreferences,
  useCreateDietaryPreference,
  useIngredients,
  useCreateIngredient,
  useRecipeTags,
  useCreateRecipeTag,
  useUpdateCatalogItem,
  useDeleteCatalogItem,
  type MedicalCondition,
  type FoodIntolerance,
  type DietaryPreference,
  type Ingredient,
  type RecipeTag
} from '@/lib/hooks/useCatalogs';
import { Plus, Edit, Trash2, Heart, AlertTriangle, Utensils, Package, Tag, AlertCircle } from 'lucide-react';

type CatalogTab = 'conditions' | 'intolerances' | 'preferences' | 'ingredients' | 'tags';

export default function CatalogsPage() {
  const [activeTab, setActiveTab] = useState<CatalogTab>('conditions');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState<any>(null);

  const tabs = [
    { id: 'conditions' as CatalogTab, label: 'Medical Conditions', icon: Heart, color: 'text-red-500' },
    { id: 'intolerances' as CatalogTab, label: 'Food Intolerances', icon: AlertTriangle, color: 'text-orange-500' },
    { id: 'preferences' as CatalogTab, label: 'Dietary Preferences', icon: Utensils, color: 'text-green-500' },
    { id: 'ingredients' as CatalogTab, label: 'Ingredients', icon: Package, color: 'text-blue-500' },
    { id: 'tags' as CatalogTab, label: 'Recipe Tags', icon: Tag, color: 'text-purple-500' }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'conditions':
        return <MedicalConditionsTab onEdit={handleEdit} onDelete={handleDelete} />;
      case 'intolerances':
        return <FoodIntolerancesTab onEdit={handleEdit} onDelete={handleDelete} />;
      case 'preferences':
        return <DietaryPreferencesTab onEdit={handleEdit} onDelete={handleDelete} />;
      case 'ingredients':
        return <IngredientsTab onEdit={handleEdit} onDelete={handleDelete} />;
      case 'tags':
        return <RecipeTagsTab onEdit={handleEdit} onDelete={handleDelete} />;
      default:
        return null;
    }
  };

  const handleEdit = (item: any) => {
    setSelectedItem(item);
    setShowEditModal(true);
  };

  const handleDelete = async (item: any) => {
    // Handle delete logic here
    console.log('Delete:', item);
  };

  return (
    <AuthenticatedLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Catalogs</h1>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Item
        </Button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap
                  ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <Icon className={`w-4 h-4 mr-2 ${tab.color}`} />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {renderTabContent()}

      {/* Create Modal */}
      {showCreateModal && (
        <CreateItemModal
          catalogType={activeTab}
          onClose={() => setShowCreateModal(false)}
        />
      )}

      {/* Edit Modal */}
      {showEditModal && selectedItem && (
        <EditItemModal
          catalogType={activeTab}
          item={selectedItem}
          onClose={() => {
            setShowEditModal(false);
            setSelectedItem(null);
          }}
        />
      )}
      </div>
    </AuthenticatedLayout>
  );
}

// Medical Conditions Tab
function MedicalConditionsTab({ onEdit, onDelete }: { onEdit: (item: any) => void; onDelete: (item: any) => void }) {
  const { data, loading, error, refetch } = useMedicalConditions();
  const { deleteItem } = useDeleteCatalogItem();

  const conditions = Array.isArray(data?.medical_conditions) ? data.medical_conditions : [];

  const handleDelete = async (condition: MedicalCondition) => {
    if (confirm(`Are you sure you want to delete "${condition.condition_name}"?`)) {
      try {
        await deleteItem('medical-conditions', condition.id);
        refetch();
      } catch (error) {
        console.error('Failed to delete condition:', error);
      }
    }
  };

  const getSeverityBadge = (severity: string) => {
    const colors = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800'
    };
    return <span className={`px-2 py-1 text-xs font-medium rounded-full ${colors[severity as keyof typeof colors] || colors.medium}`}>
      {severity}
    </span>;
  };

  const columns = [
    { key: 'condition_name', title: 'Condition Name' },
    { key: 'description', title: 'Description', render: (desc: string) => desc || '-' },
    { 
      key: 'severity_level', 
      title: 'Severity',
      render: (severity: string) => getSeverityBadge(severity)
    },
    { key: 'created_at', title: 'Created', render: (date: string) => new Date(date).toLocaleDateString() },
    {
      key: 'actions',
      title: 'Actions',
      render: (_: any, record: MedicalCondition) => (
        <div className="flex space-x-2">
          <Button size="sm" variant="ghost" onClick={() => onEdit(record)}>
            <Edit className="w-4 h-4" />
          </Button>
          <Button size="sm" variant="ghost" onClick={() => handleDelete(record)}>
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      )
    }
  ];

  if (error) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p className="text-gray-500">{error}</p>
      </div>
    );
  }

  return (
    <Card>
      <DataTable
        columns={columns}
        data={conditions}
        loading={loading}
        emptyMessage="No medical conditions found"
      />
    </Card>
  );
}

// Food Intolerances Tab
function FoodIntolerancesTab({ onEdit, onDelete }: { onEdit: (item: any) => void; onDelete: (item: any) => void }) {
  const { data, loading, error, refetch } = useFoodIntolerances();
  const { deleteItem } = useDeleteCatalogItem();

  const intolerances = Array.isArray(data?.food_intolerances) ? data.food_intolerances : [];

  const handleDelete = async (intolerance: FoodIntolerance) => {
    if (confirm(`Are you sure you want to delete "${intolerance.intolerance_name}"?`)) {
      try {
        await deleteItem('food-intolerances', intolerance.id);
        refetch();
      } catch (error) {
        console.error('Failed to delete intolerance:', error);
      }
    }
  };

  const columns = [
    { key: 'intolerance_name', title: 'Intolerance Name' },
    { key: 'description', title: 'Description', render: (desc: string) => desc || '-' },
    { key: 'created_at', title: 'Created', render: (date: string) => new Date(date).toLocaleDateString() },
    {
      key: 'actions',
      title: 'Actions',
      render: (_: any, record: FoodIntolerance) => (
        <div className="flex space-x-2">
          <Button size="sm" variant="ghost" onClick={() => onEdit(record)}>
            <Edit className="w-4 h-4" />
          </Button>
          <Button size="sm" variant="ghost" onClick={() => handleDelete(record)}>
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      )
    }
  ];

  if (error) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p className="text-gray-500">{error}</p>
      </div>
    );
  }

  return (
    <Card>
      <DataTable
        columns={columns}
        data={intolerances}
        loading={loading}
        emptyMessage="No food intolerances found"
      />
    </Card>
  );
}

// Dietary Preferences Tab
function DietaryPreferencesTab({ onEdit, onDelete }: { onEdit: (item: any) => void; onDelete: (item: any) => void }) {
  const { data, loading, error, refetch } = useDietaryPreferences();
  const { deleteItem } = useDeleteCatalogItem();

  const preferences = Array.isArray(data?.dietary_preferences) ? data.dietary_preferences : [];

  const handleDelete = async (preference: DietaryPreference) => {
    if (confirm(`Are you sure you want to delete "${preference.preference_name}"?`)) {
      try {
        await deleteItem('dietary-preferences', preference.id);
        refetch();
      } catch (error) {
        console.error('Failed to delete preference:', error);
      }
    }
  };

  const columns = [
    { key: 'preference_name', title: 'Preference Name' },
    { key: 'description', title: 'Description', render: (desc: string) => desc || '-' },
    { key: 'created_at', title: 'Created', render: (date: string) => new Date(date).toLocaleDateString() },
    {
      key: 'actions',
      title: 'Actions',
      render: (_: any, record: DietaryPreference) => (
        <div className="flex space-x-2">
          <Button size="sm" variant="ghost" onClick={() => onEdit(record)}>
            <Edit className="w-4 h-4" />
          </Button>
          <Button size="sm" variant="ghost" onClick={() => handleDelete(record)}>
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      )
    }
  ];

  if (error) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p className="text-gray-500">{error}</p>
      </div>
    );
  }

  return (
    <Card>
      <DataTable
        columns={columns}
        data={preferences}
        loading={loading}
        emptyMessage="No dietary preferences found"
      />
    </Card>
  );
}

// Ingredients Tab
function IngredientsTab({ onEdit, onDelete }: { onEdit: (item: any) => void; onDelete: (item: any) => void }) {
  const { data, loading, error, refetch } = useIngredients();
  const { deleteItem } = useDeleteCatalogItem();

  const ingredients = Array.isArray(data?.ingredients) ? data.ingredients : [];

  const handleDelete = async (ingredient: Ingredient) => {
    if (confirm(`Are you sure you want to delete "${ingredient.ingredient_name}"?`)) {
      try {
        await deleteItem('ingredients', ingredient.id);
        refetch();
      } catch (error) {
        console.error('Failed to delete ingredient:', error);
      }
    }
  };

  const columns = [
    { key: 'ingredient_name', title: 'Ingredient Name' },
    { key: 'category', title: 'Category', render: (cat: string) => cat || '-' },
    { 
      key: 'calories_per_100g', 
      title: 'Calories/100g',
      render: (cal: number) => cal ? `${cal} kcal` : '-'
    },
    { 
      key: 'protein_per_100g', 
      title: 'Protein/100g',
      render: (protein: number) => protein ? `${protein}g` : '-'
    },
    { key: 'created_at', title: 'Created', render: (date: string) => new Date(date).toLocaleDateString() },
    {
      key: 'actions',
      title: 'Actions',
      render: (_: any, record: Ingredient) => (
        <div className="flex space-x-2">
          <Button size="sm" variant="ghost" onClick={() => onEdit(record)}>
            <Edit className="w-4 h-4" />
          </Button>
          <Button size="sm" variant="ghost" onClick={() => handleDelete(record)}>
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      )
    }
  ];

  if (error) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p className="text-gray-500">{error}</p>
      </div>
    );
  }

  return (
    <Card>
      <DataTable
        columns={columns}
        data={ingredients}
        loading={loading}
        emptyMessage="No ingredients found"
      />
    </Card>
  );
}

// Recipe Tags Tab
function RecipeTagsTab({ onEdit, onDelete }: { onEdit: (item: any) => void; onDelete: (item: any) => void }) {
  const { data, loading, error, refetch } = useRecipeTags();
  const { deleteItem } = useDeleteCatalogItem();

  const tags = Array.isArray(data?.recipe_tags) ? data.recipe_tags : [];

  const handleDelete = async (tag: RecipeTag) => {
    if (confirm(`Are you sure you want to delete "${tag.tag_name}"?`)) {
      try {
        await deleteItem('recipe-tags', tag.id);
        refetch();
      } catch (error) {
        console.error('Failed to delete tag:', error);
      }
    }
  };

  const columns = [
    { 
      key: 'tag_name', 
      title: 'Tag Name',
      render: (name: string, record: RecipeTag) => (
        <div className="flex items-center">
          <div
            className="w-4 h-4 rounded-full mr-2"
            style={{ backgroundColor: record.color }}
          />
          {name}
        </div>
      )
    },
    { key: 'color', title: 'Color' },
    { key: 'created_at', title: 'Created', render: (date: string) => new Date(date).toLocaleDateString() },
    {
      key: 'actions',
      title: 'Actions',
      render: (_: any, record: RecipeTag) => (
        <div className="flex space-x-2">
          <Button size="sm" variant="ghost" onClick={() => onEdit(record)}>
            <Edit className="w-4 h-4" />
          </Button>
          <Button size="sm" variant="ghost" onClick={() => handleDelete(record)}>
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      )
    }
  ];

  if (error) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <p className="text-gray-500">{error}</p>
      </div>
    );
  }

  return (
    <Card>
      <DataTable
        columns={columns}
        data={tags}
        loading={loading}
        emptyMessage="No recipe tags found"
      />
    </Card>
  );
}

// Create Item Modal
function CreateItemModal({ catalogType, onClose }: { catalogType: CatalogTab; onClose: () => void }) {
  return (
    <Modal open={true} onClose={onClose} title="Create Item" size="md">
      <div className="py-4">
        <p>Create form for {catalogType} will be implemented here</p>
        <ModalFooter>
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button>Create</Button>
        </ModalFooter>
      </div>
    </Modal>
  );
}

// Edit Item Modal
function EditItemModal({ catalogType, item, onClose }: { catalogType: CatalogTab; item: any; onClose: () => void }) {
  return (
    <Modal open={true} onClose={onClose} title="Edit Item" size="md">
      <div className="py-4">
        <p>Edit form for {catalogType} will be implemented here</p>
        <p>Editing: {JSON.stringify(item, null, 2)}</p>
        <ModalFooter>
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button>Save Changes</Button>
        </ModalFooter>
      </div>
    </Modal>
  );
}
