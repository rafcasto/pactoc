import { useState, useEffect } from 'react';
import { useApi } from './useApi';
import { apiClient } from '@/lib/firebase/api';

export interface Patient {
  id: string;
  invitation_id?: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: 'male' | 'female' | 'other';
  email?: string;
  phone?: string;
  profile_status: 'pending_review' | 'approved';
  additional_notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  conditions_count?: number;
  intolerances_count?: number;
  preferences_count?: number;
  medical_conditions?: MedicalCondition[];
  intolerances?: Intolerance[];
  dietary_preferences?: DietaryPreference[];
}

export interface MedicalCondition {
  id: string;
  condition_id: string;
  condition_name: string;
  notes?: string;
  added_at: string;
}

export interface Intolerance {
  id: string;
  intolerance_id: string;
  intolerance_name: string;
  severity: 'mild' | 'moderate' | 'severe';
  notes?: string;
  added_at: string;
}

export interface DietaryPreference {
  id: string;
  preference_id: string;
  preference_name: string;
  added_at: string;
}

export interface PatientStats {
  total: number;
  active: number;
  pending_review: number;
  approved: number;
  inactive: number;
}

// Get all patients
export function usePatients(filters?: {
  profile_status?: string;
  is_active?: boolean;
  search?: string;
}) {
  const [data, setData] = useState<{ patients: Patient[]; total: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPatients = async () => {
    setLoading(true);
    setError(null);
    
    try {
      let endpoint = '/patients';
      
      if (filters) {
        const params = new URLSearchParams();
        if (filters.profile_status) params.append('profile_status', filters.profile_status);
        if (filters.is_active !== undefined) params.append('is_active', filters.is_active.toString());
        if (filters.search) params.append('search', filters.search);
        
        if (params.toString()) {
          endpoint += `?${params.toString()}`;
        }
      }
      
      const result = await apiClient.get<{ patients: Patient[]; total: number }>(endpoint);
      
      // Filter data locally if needed since our simple backend doesn't filter
      let filteredPatients = result.patients;
      
      if (filters?.profile_status) {
        filteredPatients = filteredPatients.filter((p: Patient) => p.profile_status === filters.profile_status);
      }
      
      if (filters?.search) {
        const searchTerm = filters.search.toLowerCase();
        filteredPatients = filteredPatients.filter((p: Patient) => 
          p.first_name.toLowerCase().includes(searchTerm) ||
          p.last_name.toLowerCase().includes(searchTerm) ||
          (p.email && p.email.toLowerCase().includes(searchTerm))
        );
      }
      
      setData({ patients: filteredPatients, total: filteredPatients.length });
    } catch (err: any) {
      setError(err.message || 'Failed to fetch patients');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, [filters?.profile_status, filters?.search]);

  return { data, loading, error, refetch: fetchPatients };
}

// Get single patient
export function usePatient(patientId: string) {
  return useApi<{ patient: Patient }>(`/api/patients/${patientId}`);
}

// Get patient stats
export function usePatientStats() {
  const [data, setData] = useState<{ stats: PatientStats } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiClient.get<{ stats: PatientStats }>('/patients/stats');
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch patient stats');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return { data, loading, error, refetch: fetchStats };
}

// Update patient mutation
export function useUpdatePatient() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updatePatient = async (patientId: string, data: Partial<Patient>) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.put<{ patient: Patient }>(`/api/patients/${patientId}`, data as unknown as Record<string, unknown>);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to update patient');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { updatePatient, loading, error };
}

// Update patient status mutation
export function useUpdatePatientStatus() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateStatus = async (patientId: string, status: 'pending_review' | 'approved') => {
    setLoading(true);
    setError(null);

    try {
      // Mock the status update
      console.log(`Updated patient ${patientId} status to ${status}`);
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      return true;
    } catch (err: any) {
      setError(err.message || 'Failed to update patient status');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { updateStatus, loading, error };
}

// Delete patient mutation
export function useDeletePatient() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const deletePatient = async (patientId: string) => {
    setLoading(true);
    setError(null);

    try {
      // Mock the patient deletion
      console.log(`Deleted patient ${patientId}`);
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      return true;
    } catch (err: any) {
      setError(err.message || 'Failed to delete patient');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { deletePatient, loading, error };
}

// Add condition to patient
export function useAddPatientCondition() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addCondition = async (patientId: string, conditionData: {
    condition_id: string;
    condition_name: string;
    notes?: string;
  }) => {
    setLoading(true);
    setError(null);

    try {
      await apiClient.post(`/api/patients/${patientId}/conditions`, conditionData as unknown as Record<string, unknown>);
      return true;
    } catch (err: any) {
      setError(err.message || 'Failed to add condition');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { addCondition, loading, error };
}

// Remove condition from patient
export function useRemovePatientCondition() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const removeCondition = async (patientId: string, conditionDocId: string) => {
    setLoading(true);
    setError(null);

    try {
      await apiClient.delete(`/api/patients/${patientId}/conditions/${conditionDocId}`);
      return true;
    } catch (err: any) {
      setError(err.message || 'Failed to remove condition');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { removeCondition, loading, error };
}
