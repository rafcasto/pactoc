import { useState, useEffect } from 'react';
import { PatientMealPlanView, PatientMealPlanSummary } from '@/types/business-rules';

const API_BASE = 'http://localhost:5001/api/patient';

// Hook for patient meal plan (patient view - only latest approved version)
export function usePatientMealPlan(token: string) {
  const [mealPlanData, setMealPlanData] = useState<PatientMealPlanView | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMealPlan = async () => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/meal-plan/${token}`, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        setMealPlanData(result.data);
      } else {
        setError(result.message);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch meal plan');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMealPlan();
  }, [token]);

  return {
    mealPlanData,
    loading,
    error,
    refetch: fetchMealPlan
  };
}

// Hook for patient meal plan summary
export function usePatientMealPlanSummary(token: string) {
  const [summary, setSummary] = useState<PatientMealPlanSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = async () => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/meal-plan/${token}/summary`, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        setSummary(result.data);
      } else {
        setError(result.message);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to fetch meal plan summary');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, [token]);

  return {
    summary,
    loading,
    error,
    refetch: fetchSummary
  };
}
