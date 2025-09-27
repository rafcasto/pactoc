import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/components/auth/AuthProvider';
import { apiClient } from '@/lib/firebase/api';

interface ApiError {
  message: string;
}

export function useApi<T>(endpoint: string, immediate = true) {
  const { user, loading: authLoading } = useAuth();
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async () => {
    if (authLoading || !user) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.get<T>(endpoint);
      setData(result);
    } catch (err) {
      const error = err as ApiError;
      setError(error.message || 'API request failed');
    } finally {
      setLoading(false);
    }
  }, [endpoint, user, authLoading]);

  useEffect(() => {
    if (immediate && !authLoading && user) {
      execute();
    }
  }, [immediate, user, authLoading, execute]);

  return { data, loading: loading || authLoading, error, refetch: execute };
}