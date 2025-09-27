'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/components/auth/AuthProvider';
import { apiClient } from '@/lib/firebase/api';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

interface DashboardData {
  message: string;
  user: {
    uid: string;
    email: string;
    name: string;
  };
  auth_time: number;
}

interface ApiError {
  message: string;
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await apiClient.get<DashboardData>('/auth/hello');
      setDashboardData(data);
    } catch (err) {
      const error = err as ApiError;
      setError(error.message || 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const testProtectedEndpoint = async () => {
    setLoading(true);
    setError(null);

    try {
      const testData = { message: 'Test from frontend', timestamp: Date.now() };
      const response = await apiClient.post('/auth/protected', testData);
      console.log('Protected endpoint response:', response);
      alert('Protected endpoint test successful! Check console for details.');
    } catch (err) {
      const error = err as ApiError;
      setError(error.message || 'Failed to test protected endpoint');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Welcome to your authenticated dashboard!
          </p>
        </div>

        {/* User Info Card */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">User Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <p className="mt-1 text-sm text-gray-900">{user?.email}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Display Name
              </label>
              <p className="mt-1 text-sm text-gray-900">
                {user?.displayName || 'Not set'}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                User ID
              </label>
              <p className="mt-1 text-sm text-gray-900 font-mono">{user?.uid}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Email Verified
              </label>
              <p className="mt-1 text-sm text-gray-900">
                {user?.emailVerified ? 'Yes' : 'No'}
              </p>
            </div>
          </div>
        </Card>

        {/* API Test Card */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Backend API Test</h2>
          
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-4">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          <div className="space-y-4">
            <div className="flex space-x-4">
              <Button
                onClick={fetchDashboardData}
                loading={loading}
                disabled={loading}
              >
                Test GET /auth/hello
              </Button>
              
              <Button
                onClick={testProtectedEndpoint}
                loading={loading}
                disabled={loading}
                variant="outline"
              >
                Test POST /auth/protected
              </Button>
            </div>

            {dashboardData && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
                <h3 className="text-sm font-medium text-green-800 mb-2">
                  Backend Response:
                </h3>
                <pre className="text-xs text-green-700 whitespace-pre-wrap">
                  {JSON.stringify(dashboardData, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </Card>

        {/* Quick Actions */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="flex space-x-4">
            <Button
              onClick={() => window.location.href = '/profile'}
              variant="outline"
            >
              View Profile
            </Button>
            <Button
              onClick={() => window.open('https://console.firebase.google.com/', '_blank')}
              variant="outline"
            >
              Firebase Console
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
