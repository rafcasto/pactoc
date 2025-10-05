import { useState, useEffect } from 'react';
import { useApi } from './useApi';
import { apiClient } from '@/lib/firebase/api';

const API_BASE_URL = 'http://localhost:8000';

export interface Invitation {
  id: string;
  token: string;
  email: string;
  first_name?: string;
  last_name?: string;
  invited_by_uid: string;
  status: 'pending' | 'completed' | 'expired';
  expires_at: string;
  created_at: string;
  public_link?: string;
}

export interface CreateInvitationData {
  email: string;
  first_name?: string;
  last_name?: string;
}

export interface InvitationStats {
  total: number;
  pending: number;
  completed: number;
  expired: number;
}

// Get all invitations
export function useInvitations(status?: string) {
  const [data, setData] = useState<{ invitations: Invitation[]; total: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInvitations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const endpoint = status ? `/invitations?status=${status}` : '/invitations';
      const result = await apiClient.get<{ invitations: Invitation[]; total: number }>(endpoint);
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch invitations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvitations();
  }, [status]);

  return { data, loading, error, refetch: fetchInvitations };
}

// Get invitation stats  
export function useInvitationStats() {
  // Mock stats for now since our simple backend doesn't have this endpoint
  return {
    data: {
      stats: {
        total: 1,
        pending: 1,
        completed: 0,
        expired: 0
      }
    },
    loading: false,
    error: null
  };
}

// Create invitation mutation
export function useCreateInvitation() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createInvitation = async (data: CreateInvitationData) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.post<{ invitation: Invitation; public_link: string }>('/invitations', data as unknown as Record<string, unknown>);
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to create invitation');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createInvitation, loading, error };
}

// Resend invitation mutation
export function useResendInvitation() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resendInvitation = async (invitationId: string) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.post<{ invitation: Invitation }>(`/invitations/resend/${invitationId}`, {});
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to resend invitation');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { resendInvitation, loading, error };
}

// Regenerate invitation link mutation
export function useRegenerateInvitation() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const regenerateInvitation = async (invitationId: string) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.post<{ invitation: Invitation; public_link: string }>(`/invitations/regenerate/${invitationId}`, {});
      return result;
    } catch (err: any) {
      setError(err.message || 'Failed to regenerate invitation');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { regenerateInvitation, loading, error };
}

// Cancel invitation mutation
export function useCancelInvitation() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cancelInvitation = async (invitationId: string) => {
    setLoading(true);
    setError(null);

    try {
      await apiClient.delete(`/invitations/${invitationId}`);
      return true;
    } catch (err: any) {
      setError(err.message || 'Failed to cancel invitation');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { cancelInvitation, loading, error };
}
