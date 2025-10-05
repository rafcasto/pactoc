'use client';

import React, { useState } from 'react';
import { AuthenticatedLayout } from '@/components/layout/AuthenticatedLayout';
import { Metadata } from 'next';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Modal, ModalFooter } from '@/components/ui/Modal';
import { useMealPlans, useCreateMealPlan, useUpdateMealPlan, useDeleteMealPlan, type MealPlan, type CreateMealPlanData } from '@/lib/hooks/useMealPlans';
import { Plus, Search, Calendar, Users, ChefHat, Clock, AlertCircle, Edit, Trash2, Eye } from 'lucide-react';

export default function MealPlansPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPatient, setSelectedPatient] = useState<string>('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedMealPlan, setSelectedMealPlan] = useState<MealPlan | null>(null);

  // Hooks
  const { data: mealPlansData, loading, error, refetch } = useMealPlans({
    search: searchTerm || undefined,
    patient_id: selectedPatient || undefined
  });
  const { createMealPlan, loading: creating } = useCreateMealPlan();
  const { updateMealPlan, loading: updating } = useUpdateMealPlan();
  const { deleteMealPlan, loading: deleting } = useDeleteMealPlan();

  const mealPlans = mealPlansData?.meal_plans || [];

  const handleCreateMealPlan = async (data: CreateMealPlanData | Partial<CreateMealPlanData>) => {
    // For create, we ensure we have complete data
    const createData = data as CreateMealPlanData;
    try {
      await createMealPlan(createData);
      setShowCreateModal(false);
      refetch();
    } catch (error) {
      console.error('Failed to create meal plan:', error);
    }
  };

  const handleUpdateMealPlan = async (data: CreateMealPlanData | Partial<CreateMealPlanData>) => {
    if (!selectedMealPlan) return;
    
    try {
      await updateMealPlan(selectedMealPlan.id, data);
      setShowEditModal(false);
      setSelectedMealPlan(null);
      refetch();
    } catch (error) {
      console.error('Failed to update meal plan:', error);
    }
  };

  const handleDeleteMealPlan = async (mealPlan: MealPlan) => {
    if (confirm(`Are you sure you want to delete "${mealPlan.plan_name}"?`)) {
      try {
        await deleteMealPlan(mealPlan.id);
        refetch();
      } catch (error) {
        console.error('Failed to delete meal plan:', error);
      }
    }
  };

  const handleViewMealPlan = (mealPlan: MealPlan) => {
    setSelectedMealPlan(mealPlan);
    setShowViewModal(true);
  };

  const handleEditMealPlan = (mealPlan: MealPlan) => {
    setSelectedMealPlan(mealPlan);
    setShowEditModal(true);
  };

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading meal plans</h3>
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
          <h1 className="text-2xl font-bold text-gray-900">Meal Plans</h1>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Meal Plan
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-4">
            <div className="text-2xl font-bold text-gray-900">{mealPlans.length}</div>
            <div className="text-sm text-gray-500">Total Meal Plans</div>
          </Card>
          <Card className="p-4">
            <div className="text-2xl font-bold text-green-600">
              {mealPlans.filter(mp => mp.status === 'active').length}
            </div>
            <div className="text-sm text-gray-500">Active Plans</div>
          </Card>
          <Card className="p-4">
            <div className="text-2xl font-bold text-blue-600">
              {mealPlans.filter(mp => mp.status === 'draft').length}
            </div>
            <div className="text-sm text-gray-500">Draft Plans</div>
          </Card>
          <Card className="p-4">
            <div className="text-2xl font-bold text-purple-600">
              {mealPlans.filter(mp => mp.status === 'completed').length}
            </div>
            <div className="text-sm text-gray-500">Completed Plans</div>
          </Card>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              type="text"
              placeholder="Search meal plans..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <select
            value={selectedPatient}
            onChange={(e) => setSelectedPatient(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm"
          >
            <option value="">All Patients</option>
            <option value="1">John Doe</option>
            <option value="2">Jane Smith</option>
            <option value="3">Michael Johnson</option>
          </select>
        </div>

        {/* Meal Plans Grid */}
        <MealPlansGrid
          mealPlans={mealPlans}
          loading={loading}
          onView={handleViewMealPlan}
          onEdit={handleEditMealPlan}
          onDelete={handleDeleteMealPlan}
        />

        {/* Create Meal Plan Modal */}
        {showCreateModal && (
          <MealPlanFormModal
            title="Create New Meal Plan"
            onClose={() => setShowCreateModal(false)}
            onSubmit={handleCreateMealPlan}
            loading={creating}
          />
        )}

        {/* Edit Meal Plan Modal */}
        {showEditModal && selectedMealPlan && (
          <MealPlanFormModal
            title="Edit Meal Plan"
            mealPlan={selectedMealPlan}
            onClose={() => {
              setShowEditModal(false);
              setSelectedMealPlan(null);
            }}
            onSubmit={handleUpdateMealPlan}
            loading={updating}
          />
        )}

        {/* View Meal Plan Modal */}
        {showViewModal && selectedMealPlan && (
          <ViewMealPlanModal
            mealPlan={selectedMealPlan}
            onClose={() => {
              setShowViewModal(false);
              setSelectedMealPlan(null);
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

// Meal Plans Grid Component
interface MealPlansGridProps {
  mealPlans: MealPlan[];
  loading?: boolean;
  onView?: (mealPlan: MealPlan) => void;
  onEdit?: (mealPlan: MealPlan) => void;
  onDelete?: (mealPlan: MealPlan) => void;
}

function MealPlansGrid({ mealPlans, loading, onView, onEdit, onDelete }: MealPlansGridProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from({ length: 6 }).map((_, index) => (
          <Card key={index} className="p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded mb-4"></div>
            <div className="h-3 bg-gray-200 rounded mb-2 w-3/4"></div>
            <div className="h-3 bg-gray-200 rounded mb-4 w-1/2"></div>
            <div className="flex justify-between">
              <div className="h-6 bg-gray-200 rounded w-16"></div>
              <div className="h-6 bg-gray-200 rounded w-20"></div>
            </div>
          </Card>
        ))}
      </div>
    );
  }

  if (mealPlans.length === 0) {
    return (
      <div className="text-center py-12">
        <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Meal Plans</h3>
        <p className="text-gray-500">Create your first meal plan to get started!</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {mealPlans.map((mealPlan) => (
        <MealPlanCard
          key={mealPlan.id}
          mealPlan={mealPlan}
          onView={onView}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}

// Meal Plan Card Component
interface MealPlanCardProps {
  mealPlan: MealPlan;
  onView?: (mealPlan: MealPlan) => void;
  onEdit?: (mealPlan: MealPlan) => void;
  onDelete?: (mealPlan: MealPlan) => void;
}

function MealPlanCard({ mealPlan, onView, onEdit, onDelete }: MealPlanCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'draft':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Card className="p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <h3 className="font-semibold text-gray-900 text-lg">{mealPlan.plan_name}</h3>
        <span className={`px-2 py-1 text-xs font-medium rounded-full capitalize ${getStatusColor(mealPlan.status)}`}>
          {mealPlan.status}
        </span>
      </div>

      {mealPlan.description && (
        <p className="text-sm text-gray-600 mb-4 line-clamp-2">
          {mealPlan.description}
        </p>
      )}

      <div className="space-y-2 mb-4">
        <div className="flex items-center text-sm text-gray-500">
          <Users className="w-4 h-4 mr-2" />
          <span>Patient: {mealPlan.patient_name || 'Unassigned'}</span>
        </div>
        <div className="flex items-center text-sm text-gray-500">
          <Calendar className="w-4 h-4 mr-2" />
          <span>
            {new Date(mealPlan.start_date).toLocaleDateString()} - {new Date(mealPlan.end_date).toLocaleDateString()}
          </span>
        </div>
        <div className="flex items-center text-sm text-gray-500">
          <ChefHat className="w-4 h-4 mr-2" />
          <span>{mealPlan.total_recipes || 0} recipes</span>
        </div>
      </div>

      <div className="flex justify-end space-x-2">
        {onView && (
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onView(mealPlan)}
          >
            <Eye className="w-4 h-4" />
          </Button>
        )}
        {onEdit && (
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onEdit(mealPlan)}
          >
            <Edit className="w-4 h-4" />
          </Button>
        )}
        {onDelete && (
          <Button
            size="sm"
            variant="ghost"
            className="text-red-600 hover:text-red-700"
            onClick={() => onDelete(mealPlan)}
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        )}
      </div>
    </Card>
  );
}

// Meal Plan Form Modal Component
interface MealPlanFormModalProps {
  title: string;
  mealPlan?: MealPlan;
  onClose: () => void;
  onSubmit: (data: CreateMealPlanData | Partial<CreateMealPlanData>) => Promise<void>;
  loading: boolean;
}

function MealPlanFormModal({ title, mealPlan, onClose, onSubmit, loading }: MealPlanFormModalProps) {
  const [formData, setFormData] = useState({
    plan_name: mealPlan?.plan_name || '',
    description: mealPlan?.description || '',
    patient_id: mealPlan?.patient_id || '',
    start_date: mealPlan?.start_date || '',
    end_date: mealPlan?.end_date || '',
    status: mealPlan?.status || 'draft' as const,
    target_calories: mealPlan?.target_calories || 2000,
    target_protein: mealPlan?.target_protein || 150,
    target_carbs: mealPlan?.target_carbs || 250,
    target_fat: mealPlan?.target_fat || 70,
    notes: mealPlan?.notes || ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.plan_name || !formData.start_date || !formData.end_date) return;

    await onSubmit(formData);
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
              Plan Name *
            </label>
            <Input
              type="text"
              value={formData.plan_name}
              onChange={(e) => setFormData({ ...formData, plan_name: e.target.value })}
              required
              placeholder="Enter plan name..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Patient
            </label>
            <select
              value={formData.patient_id}
              onChange={(e) => setFormData({ ...formData, patient_id: e.target.value })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="">Select Patient</option>
              <option value="1">John Doe</option>
              <option value="2">Jane Smith</option>
              <option value="3">Michael Johnson</option>
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
            placeholder="Brief description of the meal plan..."
          />
        </div>

        {/* Dates and Status */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Start Date *
            </label>
            <Input
              type="date"
              value={formData.start_date}
              onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Date *
            </label>
            <Input
              type="date"
              value={formData.end_date}
              onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              <option value="draft">Draft</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
            </select>
          </div>
        </div>

        {/* Nutrition Targets */}
        <div>
          <h4 className="font-medium text-gray-900 mb-3">Daily Nutrition Targets</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Calories
              </label>
              <Input
                type="number"
                value={formData.target_calories}
                onChange={(e) => setFormData({ ...formData, target_calories: parseInt(e.target.value) || 0 })}
                min="0"
                placeholder="2000"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Protein (g)
              </label>
              <Input
                type="number"
                value={formData.target_protein}
                onChange={(e) => setFormData({ ...formData, target_protein: parseInt(e.target.value) || 0 })}
                min="0"
                placeholder="150"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Carbs (g)
              </label>
              <Input
                type="number"
                value={formData.target_carbs}
                onChange={(e) => setFormData({ ...formData, target_carbs: parseInt(e.target.value) || 0 })}
                min="0"
                placeholder="250"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fat (g)
              </label>
              <Input
                type="number"
                value={formData.target_fat}
                onChange={(e) => setFormData({ ...formData, target_fat: parseInt(e.target.value) || 0 })}
                min="0"
                placeholder="70"
              />
            </div>
          </div>
        </div>

        {/* Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notes
          </label>
          <textarea
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            rows={4}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            placeholder="Additional notes or special instructions..."
          />
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            loading={loading} 
            disabled={!formData.plan_name || !formData.start_date || !formData.end_date}
          >
            {mealPlan ? 'Update Meal Plan' : 'Create Meal Plan'}
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}

// View Meal Plan Modal Component
interface ViewMealPlanModalProps {
  mealPlan: MealPlan;
  onClose: () => void;
  onEdit: () => void;
}

function ViewMealPlanModal({ mealPlan, onClose, onEdit }: ViewMealPlanModalProps) {
  return (
    <Modal
      open={true}
      onClose={onClose}
      title={mealPlan.plan_name}
      size="xl"
    >
      <div className="space-y-6">
        {/* Basic Info */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div className="flex items-center justify-center">
            <Users className="w-5 h-5 text-gray-400 mr-2" />
            <span className="text-sm">{mealPlan.patient_name || 'Unassigned'}</span>
          </div>
          <div className="flex items-center justify-center">
            <Calendar className="w-5 h-5 text-gray-400 mr-2" />
            <span className="text-sm">
              {Math.ceil((new Date(mealPlan.end_date).getTime() - new Date(mealPlan.start_date).getTime()) / (1000 * 60 * 60 * 24))} days
            </span>
          </div>
          <div className="flex items-center justify-center">
            <ChefHat className="w-5 h-5 text-gray-400 mr-2" />
            <span className="text-sm">{mealPlan.total_recipes || 0} recipes</span>
          </div>
          <div className="flex items-center justify-center">
            <span className={`px-3 py-1 text-xs font-medium rounded-full capitalize ${
              mealPlan.status === 'active' ? 'bg-green-100 text-green-800' :
              mealPlan.status === 'draft' ? 'bg-blue-100 text-blue-800' :
              'bg-purple-100 text-purple-800'
            }`}>
              {mealPlan.status}
            </span>
          </div>
        </div>

        {/* Description */}
        {mealPlan.description && (
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Description</h4>
            <p className="text-gray-600">{mealPlan.description}</p>
          </div>
        )}

        {/* Dates */}
        <div>
          <h4 className="font-medium text-gray-900 mb-2">Duration</h4>
          <p className="text-gray-600">
            From {new Date(mealPlan.start_date).toLocaleDateString()} to {new Date(mealPlan.end_date).toLocaleDateString()}
          </p>
        </div>

        {/* Nutrition Targets */}
        <div>
          <h4 className="font-medium text-gray-900 mb-3">Daily Nutrition Targets</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="p-3 bg-red-50 rounded-lg text-center">
              <div className="text-lg font-bold text-red-600">
                {mealPlan.target_calories || 0}
                <span className="text-sm font-normal">kcal</span>
              </div>
              <div className="text-xs text-gray-600 mt-1">Calories</div>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg text-center">
              <div className="text-lg font-bold text-blue-600">
                {mealPlan.target_protein || 0}
                <span className="text-sm font-normal">g</span>
              </div>
              <div className="text-xs text-gray-600 mt-1">Protein</div>
            </div>
            <div className="p-3 bg-yellow-50 rounded-lg text-center">
              <div className="text-lg font-bold text-yellow-600">
                {mealPlan.target_carbs || 0}
                <span className="text-sm font-normal">g</span>
              </div>
              <div className="text-xs text-gray-600 mt-1">Carbs</div>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg text-center">
              <div className="text-lg font-bold text-purple-600">
                {mealPlan.target_fat || 0}
                <span className="text-sm font-normal">g</span>
              </div>
              <div className="text-xs text-gray-600 mt-1">Fat</div>
            </div>
          </div>
        </div>

        {/* Notes */}
        {mealPlan.notes && (
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Notes</h4>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-gray-700 whitespace-pre-wrap">{mealPlan.notes}</p>
            </div>
          </div>
        )}

        <ModalFooter>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
          <Button onClick={onEdit}>
            Edit Meal Plan
          </Button>
        </ModalFooter>
      </div>
    </Modal>
  );
}
