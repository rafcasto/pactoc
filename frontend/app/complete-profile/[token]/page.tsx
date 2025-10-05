'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Utensils, User, Heart, AlertCircle, ChevronRight, Loader2 } from 'lucide-react';

interface InvitationData {
  invitation_id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  expires_at: string;
}

interface CatalogItem {
  id: number;
  condition_name?: string;
  intolerance_name?: string;
  preference_name?: string;
  description: string;
  is_active: boolean;
}

interface Catalogs {
  medical_conditions: CatalogItem[];
  food_intolerances: CatalogItem[];
  dietary_preferences: CatalogItem[];
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

export default function CompleteProfile() {
  const { token } = useParams();
  const router = useRouter();
  
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [validToken, setValidToken] = useState(false);
  const [invitation, setInvitation] = useState<InvitationData | null>(null);
  const [catalogs, setCatalogs] = useState<Catalogs | null>(null);
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
      validateTokenAndLoadData();
    }
  }, [token]);

  const validateTokenAndLoadData = async () => {
    try {
      setLoading(true);
      
      // Validar token
      const tokenResponse = await fetch(`/api/public/invitations/${token}`);
      const tokenData = await tokenResponse.json();
      
      if (!tokenResponse.ok || !tokenData.valid) {
        setError(tokenData.error || 'Token inválido o expirado');
        setValidToken(false);
        return;
      }
      
      setValidToken(true);
      setInvitation(tokenData.invitation);
      
      // Pre-llenar datos si están disponibles
      if (tokenData.invitation.email) {
        setFormData(prev => ({ 
          ...prev, 
          email: tokenData.invitation.email,
          first_name: tokenData.invitation.first_name || '',
          last_name: tokenData.invitation.last_name || ''
        }));
      }
      
      // Cargar catálogos
      const catalogsResponse = await fetch('/api/public/catalogs');
      if (catalogsResponse.ok) {
        const catalogsData = await catalogsResponse.json();
        setCatalogs(catalogsData);
      }
      
    } catch (error) {
      console.error('Error validating token:', error);
      setError('Error de conexión. Intente nuevamente.');
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
    if (!formData.first_name.trim()) return 'El nombre es requerido';
    if (!formData.last_name.trim()) return 'El apellido es requerido';
    if (!formData.date_of_birth) return 'La fecha de nacimiento es requerida';
    if (!formData.gender) return 'El género es requerido';
    if (!formData.email.trim()) return 'El email es requerido';
    
    // Validar email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) return 'Email inválido';
    
    // Validar edad
    const birthDate = new Date(formData.date_of_birth);
    const today = new Date();
    const age = (today.getTime() - birthDate.getTime()) / (1000 * 60 * 60 * 24 * 365.25);
    if (age < 1 || age > 120) return 'Fecha de nacimiento inválida';
    
    // Validar que tenga al menos una condición o intolerancia
    if (formData.medical_conditions.length === 0 && formData.intolerances.length === 0) {
      return 'Debe seleccionar al menos una condición médica o intolerancia';
    }
    
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }
    
    setSubmitting(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/public/profiles/${token}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        // Redirigir al plan de comidas si se generó exitosamente
        if (data.meal_plan_token) {
          router.push(`/my-meal-plan/${data.meal_plan_token}`);
        } else {
          // Mostrar mensaje de éxito sin plan
          setError(null);
          // Redirigir a página de confirmación
          router.push('/profile-completed');
        }
      } else {
        setError(data.error || 'Error completando el perfil');
      }
      
    } catch (error) {
      console.error('Error submitting form:', error);
      setError('Error de conexión. Intente nuevamente.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Cargando formulario...</p>
        </div>
      </div>
    );
  }

  if (!validToken || error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-6">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-light text-gray-900 mb-2">Link Inválido</h1>
          <p className="text-gray-600 mb-4">
            {error || 'El link de invitación no es válido o ha expirado.'}
          </p>
          <p className="text-sm text-gray-500">
            Contacte con su nutricionista para obtener un nuevo link.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
            <Utensils className="w-8 h-8 text-blue-600" />
          </div>
          <h1 className="text-3xl font-light text-gray-900 mb-2">
            Sistema de Recetas Dietéticas
          </h1>
          <p className="text-gray-600">
            Completa tu perfil personalizado para recibir tu plan de comidas
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Información Personal */}
          <div className="bg-white rounded-2xl shadow-sm p-6">
            <div className="flex items-center mb-4">
              <User className="w-5 h-5 text-blue-600 mr-2" />
              <h2 className="text-lg font-medium text-gray-900">Información Personal</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre *
                </label>
                <input
                  type="text"
                  value={formData.first_name}
                  onChange={(e) => handleInputChange('first_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Tu nombre"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Apellido *
                </label>
                <input
                  type="text"
                  value={formData.last_name}
                  onChange={(e) => handleInputChange('last_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Tu apellido"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Fecha de Nacimiento *
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
                  Género *
                </label>
                <select
                  value={formData.gender}
                  onChange={(e) => handleInputChange('gender', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Seleccionar</option>
                  <option value="male">Masculino</option>
                  <option value="female">Femenino</option>
                  <option value="other">Otro</option>
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
                placeholder="tu@email.com"
              />
            </div>
            
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Teléfono
              </label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="+503 7777-7777"
              />
            </div>
          </div>

          {/* Condiciones Médicas */}
          {catalogs?.medical_conditions && (
            <div className="bg-white rounded-2xl shadow-sm p-6">
              <div className="flex items-center mb-4">
                <Heart className="w-5 h-5 text-red-500 mr-2" />
                <h2 className="text-lg font-medium text-gray-900">Condiciones Médicas</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {catalogs.medical_conditions.map((condition) => (
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

          {/* Intolerancias */}
          {catalogs?.food_intolerances && (
            <div className="bg-white rounded-2xl shadow-sm p-6">
              <div className="flex items-center mb-4">
                <AlertCircle className="w-5 h-5 text-orange-500 mr-2" />
                <h2 className="text-lg font-medium text-gray-900">Intolerancias Alimentarias</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {catalogs.food_intolerances.map((intolerance) => (
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

          {/* Preferencias Dietéticas */}
          {catalogs?.dietary_preferences && (
            <div className="bg-white rounded-2xl shadow-sm p-6">
              <div className="flex items-center mb-4">
                <Utensils className="w-5 h-5 text-green-600 mr-2" />
                <h2 className="text-lg font-medium text-gray-900">Preferencias Dietéticas</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {catalogs.dietary_preferences.map((preference) => (
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

          {/* Notas Adicionales */}
          <div className="bg-white rounded-2xl shadow-sm p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Notas Adicionales</h2>
            <textarea
              value={formData.additional_notes}
              onChange={(e) => handleInputChange('additional_notes', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Información adicional que consideres relevante (opcional)"
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
                <span>Generando tu plan...</span>
              </>
            ) : (
              <>
                <span>Generar Plan de Comidas</span>
                <ChevronRight className="w-5 h-5" />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
