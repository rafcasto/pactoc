'use client';

import React, { useState } from 'react';
import { AuthenticatedLayout } from '@/components/layout/AuthenticatedLayout';
import { RefreshCw, Plus, Calendar, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { DashboardStats } from '@/components/dashboard/DashboardStats';
import { QuickActions } from '@/components/dashboard/QuickActions';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { PriorityQueue } from '@/components/dashboard/PriorityQueue';
import { useDashboard } from '@/lib/hooks';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const { dashboardData, stats, loading, error, refreshData } = useDashboard();
  const [refreshing, setRefreshing] = useState(false);
  const router = useRouter();

  const handleRefresh = async () => {
    setRefreshing(true);
    await refreshData();
    setRefreshing(false);
  };

  const handleCreateInvitation = () => {
    router.push('/meal-plan-workflow?create=true');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    const isAuthError = error.includes('log in') || error.includes('authenticated');
    
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
              <h2 className="text-lg font-semibold text-red-900 mb-2">
                {isAuthError ? 'Authentication Required' : 'Error Loading Dashboard'}
              </h2>
              <p className="text-red-700 mb-4">{error}</p>
              <div className="flex gap-2 justify-center">
                {isAuthError ? (
                  <Button onClick={() => router.push('/login')} className="mr-2">
                    Go to Login
                  </Button>
                ) : null}
                <Button onClick={handleRefresh} variant="outline">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Try Again
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const currentDate = new Date();
  const greeting = (() => {
    const hour = currentDate.getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  })();

  return (
    <AuthenticatedLayout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {greeting}! 👋
              </h1>
              <p className="text-gray-600 mt-1">
                Here's what's happening with your patients today
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <Button
                onClick={handleRefresh}
                variant="outline"
                disabled={refreshing}
                className="hidden sm:flex"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button
                onClick={handleCreateInvitation}
                className="flex items-center"
              >
                <Plus className="h-4 w-4 mr-2" />
                New Invitation
              </Button>
            </div>
          </div>
          
          {/* Date and quick stats */}
          <div className="mt-4 flex items-center space-x-6 text-sm text-gray-500">
            <div className="flex items-center">
              <Calendar className="h-4 w-4 mr-1" />
              {currentDate.toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </div>
            {stats.pending_reviews > 0 && (
              <div className="flex items-center text-yellow-600">
                <TrendingUp className="h-4 w-4 mr-1" />
                {stats.pending_reviews} review{stats.pending_reviews !== 1 ? 's' : ''} pending
              </div>
            )}
          </div>
        </div>

        {/* Stats Overview */}
        <div className="mb-8">
          <DashboardStats stats={stats} loading={loading} />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Priority Queue - Takes full width on small screens, 2 cols on large */}
          <div className="lg:col-span-2">
            <PriorityQueue
              pendingReviews={dashboardData.pending_review}
              pendingInvitations={dashboardData.pending_invitations}
              approvedPlans={dashboardData.approved_plans}
              loading={loading}
            />
          </div>

          {/* Recent Activity - Side panel */}
          <div className="lg:col-span-1">
            <RecentActivity
              pendingReviews={dashboardData.pending_review}
              recentApprovals={dashboardData.approved_plans.slice(0, 5)}
              pendingInvitations={dashboardData.pending_invitations}
              loading={loading}
            />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <QuickActions onCreateInvitation={handleCreateInvitation} />
        </div>

        {/* Summary Footer */}
        <div className="mt-12 pt-8 border-t border-gray-200">
          <div className="text-center text-sm text-gray-500">
            <p>
              Dashboard last updated: {new Date().toLocaleTimeString()}
            </p>
            <p className="mt-1">
              Managing {stats.total_patients} patient{stats.total_patients !== 1 ? 's' : ''} 
              {stats.active_meal_plans > 0 && (
                <> with {stats.active_meal_plans} active meal plan{stats.active_meal_plans !== 1 ? 's' : ''}</>
              )}
            </p>
          </div>
        </div>
      </div>
    </AuthenticatedLayout>
  );
}
