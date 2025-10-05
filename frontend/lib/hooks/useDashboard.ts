import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/firebase/api';

export interface DashboardStats {
  total_patients: number;
  active_meal_plans: number;
  pending_reviews: number;
  pending_invitations: number;
  this_week_approvals: number;
  this_month_new_patients: number;
}

export interface WorkflowInvitation {
  invitation_id: number;
  patient_name: string;
  email: string;
  sent_at?: string;
  submitted_at?: string;
  approved_at?: string;
  expires_at?: string;
  patient_id?: number;
  meal_plan_id?: number;
  plan_name?: string;
  start_date?: string;
  end_date?: string;
  dynamic_link: string;
}

export interface DashboardData {
  pending_review: WorkflowInvitation[];
  approved_plans: WorkflowInvitation[];
  pending_invitations: WorkflowInvitation[];
  stats?: DashboardStats;
}

export function useDashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    pending_review: [],
    approved_plans: [],
    pending_invitations: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch from the meal plan workflow dashboard endpoint
      const data = await apiClient.get<DashboardData>('/api/workflow/dashboard');
      
      setDashboardData(data);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch dashboard data';
      
      // For development/demo purposes, show sample data instead of error
      if (process.env.NODE_ENV === 'development') {
        console.log('Using sample dashboard data for development');
        setDashboardData(getSampleDashboardData());
      } else {
        // Handle authentication errors specifically
        if (errorMessage.includes('not authenticated') || errorMessage.includes('No authorization header')) {
          setError('Please log in to view the dashboard');
        } else {
          setError(errorMessage);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  // Sample data for development/demo
  const getSampleDashboardData = (): DashboardData => {
    const now = new Date();
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    const twoDaysAgo = new Date(now.getTime() - 2 * 24 * 60 * 60 * 1000);
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

    return {
      pending_review: [
        {
          invitation_id: 1,
          patient_name: "Maria González",
          email: "maria@example.com",
          submitted_at: twoDaysAgo.toISOString(),
          patient_id: 1,
          dynamic_link: "sample-link-1"
        },
        {
          invitation_id: 2,
          patient_name: "Carlos Rodríguez",
          email: "carlos@example.com",
          submitted_at: yesterday.toISOString(),
          patient_id: 2,
          dynamic_link: "sample-link-2"
        }
      ],
      approved_plans: [
        {
          invitation_id: 3,
          patient_name: "Ana López",
          email: "ana@example.com",
          approved_at: weekAgo.toISOString(),
          meal_plan_id: 1,
          plan_name: "Mediterranean Diet Plan",
          start_date: weekAgo.toISOString(),
          end_date: new Date(weekAgo.getTime() + 30 * 24 * 60 * 60 * 1000).toISOString(),
          patient_id: 3,
          dynamic_link: "sample-link-3"
        },
        {
          invitation_id: 4,
          patient_name: "José Martín",
          email: "jose@example.com",
          approved_at: new Date(now.getTime() - 3 * 24 * 60 * 60 * 1000).toISOString(),
          meal_plan_id: 2,
          plan_name: "Low Carb Plan",
          start_date: new Date(now.getTime() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          end_date: new Date(now.getTime() + 28 * 24 * 60 * 60 * 1000).toISOString(),
          patient_id: 4,
          dynamic_link: "sample-link-4"
        }
      ],
      pending_invitations: [
        {
          invitation_id: 5,
          patient_name: "Laura Fernández",
          email: "laura@example.com",
          sent_at: yesterday.toISOString(),
          expires_at: new Date(now.getTime() + 6 * 24 * 60 * 60 * 1000).toISOString(),
          dynamic_link: "sample-link-5"
        },
        {
          invitation_id: 6,
          patient_name: "Roberto Silva",
          email: "roberto@example.com",
          sent_at: new Date(now.getTime() - 5 * 24 * 60 * 60 * 1000).toISOString(),
          expires_at: new Date(now.getTime() + 2 * 24 * 60 * 60 * 1000).toISOString(),
          dynamic_link: "sample-link-6"
        }
      ]
    };
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const refreshData = () => {
    fetchDashboardData();
  };

  // Calculate stats from the data if not provided by backend
  const calculateStats = (): DashboardStats => {
    const currentDate = new Date();
    const oneWeekAgo = new Date(currentDate.getTime() - 7 * 24 * 60 * 60 * 1000);
    const oneMonthAgo = new Date(currentDate.getTime() - 30 * 24 * 60 * 60 * 1000);

    const thisWeekApprovals = dashboardData.approved_plans.filter(plan => {
      if (!plan.approved_at) return false;
      const approvedDate = new Date(plan.approved_at);
      return approvedDate >= oneWeekAgo;
    }).length;

    const thisMonthNewPatients = dashboardData.pending_invitations.filter(invitation => {
      if (!invitation.sent_at) return false;
      const sentDate = new Date(invitation.sent_at);
      return sentDate >= oneMonthAgo;
    }).length;

    return {
      total_patients: dashboardData.approved_plans.length + dashboardData.pending_review.length,
      active_meal_plans: dashboardData.approved_plans.length,
      pending_reviews: dashboardData.pending_review.length,
      pending_invitations: dashboardData.pending_invitations.length,
      this_week_approvals: thisWeekApprovals,
      this_month_new_patients: thisMonthNewPatients
    };
  };

  const stats = dashboardData.stats || calculateStats();

  return {
    dashboardData,
    stats,
    loading,
    error,
    refreshData
  };
}
