'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { 
  Utensils, User, Heart, AlertCircle, ChevronRight, Loader2, 
  CheckCircle, Clock, PrinterIcon, FileDown, Mail
} from 'lucide-react';

interface InvitationData {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  expires_at: string;
  status: string;
}

interface CatalogItem {
  id: number;
  condition_name?: string;
  intolerance_name?: string;
  preference_name?: string;
  description: string;
  is_active: boolean;
}

interface FormData {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  email: string;
  phone: string;
  medical_conditions: number[];
  intolerances: number[];
  dietary_preferences: number[];
  additional_notes: string;
}

interface MealPlanData {
  meal_plan: {
    id: number;
    plan_name: string;
    start_date: string;
    end_date: string;
    notes: string;
  };
  patient: {
    name: string;
    email: string;
    conditions: string[];
    intolerances: string[];
    preferences: string[];
  };
  calendar: Record<string, Record<string, any[]>>;
  meals: any[];
}

interface DynamicLinkContent {
  invitation: InvitationData;
  status: string;
  content_type: string;
  data: any;
}

export default function PatientInvitationPage() {
  const { token } = useParams();
  
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [content, setContent] = useState<DynamicLinkContent | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState<FormData>({
    first_name: '',
    last_name: '',
    date_of_birth: '',
    gender: '',
    email: '',
    phone: '',
    medical_conditions: [],
    intolerances: [],
    dietary_preferences: [],
    additional_notes: ''
  });

  useEffect(() => {
    if (token) {
      loadDynamicContent();
    }
  }, [token]);

  const loadDynamicContent = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/workflow/patient/${token}`);
      const data = await response.json();
      
      if (response.ok && data.success) {
        setContent(data.data);
        
        // Pre-fill form data if it's a patient form
        if (data.data.content_type === 'patient_form' && data.data.invitation) {
          setFormData(prev => ({
            ...prev,
            email: data.data.invitation.email || '',
            first_name: data.data.invitation.first_name || '',
            last_name: data.data.invitation.last_name || ''
          }));
        }
      } else {
        setError(data.error || 'Invalid or expired invitation link');
      }
      
    } catch (error) {
      console.error('Error loading dynamic content:', error);
      setError('Connection error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleArrayToggle = (field: 'medical_conditions' | 'intolerances' | 'dietary_preferences', id: number) => {
    setFormData(prev => {
      const currentArray = prev[field];
      const isSelected = currentArray.includes(id);
      
      return {
        ...prev,
        [field]: isSelected 
          ? currentArray.filter(item => item !== id)
          : [...currentArray, id]
      };
    });
  };

  const validateForm = (): string | null => {
    if (!formData.first_name.trim()) return 'Name is required';
    if (!formData.last_name.trim()) return 'Last name is required';
    if (!formData.date_of_birth) return 'Date of birth is required';
    if (!formData.gender) return 'Gender is required';
    if (!formData.email.trim()) return 'Email is required';
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) return 'Invalid email';
    
    const birthDate = new Date(formData.date_of_birth);
    const today = new Date();
    const age = (today.getTime() - birthDate.getTime()) / (1000 * 60 * 60 * 24 * 365.25);
    if (age < 1 || age > 120) return 'Invalid date of birth';
    
    if (formData.medical_conditions.length === 0 && formData.intolerances.length === 0) {
      return 'Please select at least one medical condition or food intolerance';
    }
    
    return null;
  };

  const handleSubmitForm = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }
    
    setSubmitting(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/workflow/patient/${token}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        // Reload content to show new status
        await loadDynamicContent();
      } else {
        setError(data.error || 'Error submitting form');
      }
      
    } catch (error) {
      console.error('Error submitting form:', error);
      setError('Connection error. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadPDF = async () => {
    try {
      const response = await fetch(`/api/workflow/patient/${token}/pdf`);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `MealPlan_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Error downloading PDF');
      }
    } catch (error) {
      console.error('Error downloading PDF:', error);
      setError('Error downloading PDF');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-light text-gray-900 mb-2">Invalid Link</h1>
          <p className="text-gray-600 mb-4">{error}</p>
          <p className="text-sm text-gray-500">
            Please contact your nutritionist for a new link.
          </p>
        </div>
      </div>
    );
  }

  if (!content) {
    return null;
  }

  // Render based on content type
  switch (content.content_type) {
    case 'patient_form':
      return renderPatientForm();
    case 'pending_review':
      return renderPendingReview();
    case 'meal_plan':
      return renderMealPlan();
    default:
      return renderError('Unknown content type');
  }

  function renderPatientForm() {
    const catalogs = content?.data;
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
              <Utensils className="w-8 h-8 text-blue-600" />
            </div>
            <h1 className="text-3xl font-light text-gray-900 mb-2">
              Dietary Meal Plan System
            </h1>
            <p className="text-gray-600">
              Complete your personalized profile to receive your meal plan
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmitForm} className="space-y-6">
            {/* Personal Information */}
            <div className="bg-white rounded-2xl shadow-sm p-6">
              <div className="flex items-center mb-4">
                <User className="w-5 h-5 text-blue-600 mr-2" />
                <h2 className="text-lg font-medium text-gray-900">Personal Information</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    First Name *
                  </label>
                  <input
                    type="text"
                    value={formData.first_name}
                    onChange={(e) => handleInputChange('first_name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Your first name"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Last Name *
                  </label>
                  <input
                    type="text"
                    value={formData.last_name}
                    onChange={(e) => handleInputChange('last_name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Your last name"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date of Birth *
                  </label>
                  <input
                    type="date"
                    value={formData.date_of_birth}
                    onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Gender *
                  </label>
                  <select
                    value={formData.gender}
                    onChange={(e) => handleInputChange('gender', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Select</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
              
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email *
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="your@email.com"
                />
              </div>
              
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone
                </label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="+1 (555) 123-4567"
                />
              </div>
            </div>

            {/* Medical Conditions */}
            {catalogs?.medical_conditions && (
              <div className="bg-white rounded-2xl shadow-sm p-6">
                <div className="flex items-center mb-4">
                  <Heart className="w-5 h-5 text-red-500 mr-2" />
                  <h2 className="text-lg font-medium text-gray-900">Medical Conditions</h2>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {catalogs.medical_conditions.map((condition: CatalogItem) => (
                    <label key={condition.id} className="flex items-center p-3 border border-gray-200 rounded-lg hover:border-red-300 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.medical_conditions.includes(condition.id)}
                        onChange={() => handleArrayToggle('medical_conditions', condition.id)}
                        className="w-4 h-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">{condition.condition_name}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Food Intolerances */}
            {catalogs?.food_intolerances && (
              <div className="bg-white rounded-2xl shadow-sm p-6">
                <div className="flex items-center mb-4">
                  <AlertCircle className="w-5 h-5 text-orange-500 mr-2" />
                  <h2 className="text-lg font-medium text-gray-900">Food Intolerances</h2>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {catalogs.food_intolerances.map((intolerance: CatalogItem) => (
                    <label key={intolerance.id} className="flex items-center p-3 border border-gray-200 rounded-lg hover:border-orange-300 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.intolerances.includes(intolerance.id)}
                        onChange={() => handleArrayToggle('intolerances', intolerance.id)}
                        className="w-4 h-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">{intolerance.intolerance_name}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Dietary Preferences */}
            {catalogs?.dietary_preferences && (
              <div className="bg-white rounded-2xl shadow-sm p-6">
                <div className="flex items-center mb-4">
                  <Utensils className="w-5 h-5 text-green-600 mr-2" />
                  <h2 className="text-lg font-medium text-gray-900">Dietary Preferences</h2>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {catalogs.dietary_preferences.map((preference: CatalogItem) => (
                    <label key={preference.id} className="flex items-center p-3 border border-gray-200 rounded-lg hover:border-green-300 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.dietary_preferences.includes(preference.id)}
                        onChange={() => handleArrayToggle('dietary_preferences', preference.id)}
                        className="w-4 h-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">{preference.preference_name}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Additional Notes */}
            <div className="bg-white rounded-2xl shadow-sm p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Additional Notes</h2>
              <textarea
                value={formData.additional_notes}
                onChange={(e) => handleInputChange('additional_notes', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Any additional information you think is relevant (optional)"
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex">
                  <AlertCircle className="w-5 h-5 text-red-400 mr-2 mt-0.5" />
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-4 px-6 rounded-xl flex items-center justify-center space-x-2 transition-colors"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Submitting...</span>
                </>
              ) : (
                <>
                  <span>Submit Information</span>
                  <ChevronRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    );
  }

  function renderPendingReview() {
    const data = content?.data;
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-yellow-100 rounded-full mb-4">
            <Clock className="w-8 h-8 text-yellow-600" />
          </div>
          <h1 className="text-2xl font-light text-gray-900 mb-2">
            Under Review
          </h1>
          <p className="text-gray-600 mb-4">
            {data?.message || 'Your meal plan is being reviewed and will be ready soon.'}
          </p>
          <p className="text-sm text-gray-500">
            You'll receive a notification once your personalized meal plan is approved.
            Thank you for your patience!
          </p>
        </div>
      </div>
    );
  }

  function renderMealPlan() {
    const mealPlanData: MealPlanData = content?.data;
    const { meal_plan, patient, calendar } = mealPlanData;
    
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Print Styles */}
        <style jsx>{`
          @media print {
            .no-print { display: none !important; }
            .print-page { page-break-after: always; }
            body { background: white !important; }
            .meal-day { page-break-inside: avoid; }
          }
        `}</style>
        
        {/* Action Bar - No Print */}
        <div className="no-print bg-white border-b sticky top-0 z-10">
          <div className="max-w-4xl mx-auto px-6 py-4">
            <div className="flex justify-between items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Your Personalized Meal Plan
              </h1>
              <div className="flex space-x-3">
                <button
                  onClick={handlePrint}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  <PrinterIcon className="w-4 h-4 mr-2" />
                  Print
                </button>
                <button
                  onClick={handleDownloadPDF}
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
                >
                  <FileDown className="w-4 h-4 mr-2" />
                  Download PDF
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Meal Plan Content */}
        <div className="max-w-4xl mx-auto px-6 py-8">
          {/* Header */}
          <div className="bg-white rounded-2xl shadow-sm p-8 mb-8">
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                <Utensils className="w-8 h-8 text-green-600" />
              </div>
              <h1 className="text-3xl font-light text-gray-900 mb-2">
                {meal_plan.plan_name}
              </h1>
              <p className="text-gray-600">
                {new Date(meal_plan.start_date).toLocaleDateString()} - {new Date(meal_plan.end_date).toLocaleDateString()}
              </p>
            </div>
            
            {/* Patient Info */}
            <div className="border-t pt-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Patient Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-500">Patient</p>
                  <p className="text-gray-900">{patient.name}</p>
                </div>
                {patient.conditions.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Medical Conditions</p>
                    <p className="text-gray-900">{patient.conditions.join(', ')}</p>
                  </div>
                )}
                {patient.intolerances.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Food Intolerances</p>
                    <p className="text-gray-900">{patient.intolerances.join(', ')}</p>
                  </div>
                )}
              </div>
              
              {patient.preferences.length > 0 && (
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-500">Dietary Preferences</p>
                  <p className="text-gray-900">{patient.preferences.join(', ')}</p>
                </div>
              )}
            </div>
            
            {meal_plan.notes && (
              <div className="border-t pt-6 mt-6">
                <h2 className="text-lg font-medium text-gray-900 mb-2">Nutritionist Notes</h2>
                <p className="text-gray-700">{meal_plan.notes}</p>
              </div>
            )}
          </div>

          {/* Weekly Schedule */}
          <div className="bg-white rounded-2xl shadow-sm p-8">
            <h2 className="text-2xl font-light text-gray-900 mb-6">Weekly Meal Schedule</h2>
            
            <div className="space-y-8">
              {Object.entries(calendar).map(([day, meals]) => (
                <div key={day} className="meal-day">
                  <h3 className="text-xl font-medium text-gray-900 mb-4 capitalize">
                    {day}
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {Object.entries(meals).map(([mealType, mealList]) => {
                      if (mealList.length === 0) return null;
                      
                      return (
                        <div key={mealType} className="border border-gray-200 rounded-lg p-4">
                          <h4 className="font-medium text-gray-900 mb-2 capitalize">
                            {mealType}
                          </h4>
                          {Array.isArray(mealList) && mealList.map((meal: any, index: number) => (
                            <div key={index} className="mb-2 last:mb-0">
                              <p className="text-sm font-medium text-gray-800">
                                {meal.recipe_name || 'Recipe'}
                              </p>
                              {meal.scheduled_time && (
                                <p className="text-xs text-gray-500">
                                  {meal.scheduled_time}
                                </p>
                              )}
                              {meal.calories_per_serving && (
                                <p className="text-xs text-gray-500">
                                  {Math.round(meal.calories_per_serving)} calories
                                </p>
                              )}
                            </div>
                          ))}
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  function renderError(message: string) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-light text-gray-900 mb-2">Error</h1>
          <p className="text-gray-600">{message}</p>
        </div>
      </div>
    );
  }
}
