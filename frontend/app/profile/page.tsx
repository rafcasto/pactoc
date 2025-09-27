'use client';

import { useState, useEffect, useCallback } from 'react';
import Image from 'next/image';
import { useAuth } from '@/components/auth/AuthProvider';
import { apiClient } from '@/lib/firebase/api';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

interface UserProfile {
  uid: string;
  email: string;
  email_verified: boolean;
  name: string | null;
  picture: string | null;
  auth_time: number;
  firebase?: Record<string, unknown>;
}

interface ApiError {
  message: string;
}

export default function ProfilePage() {
  const { user, loading: authLoading } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  const fetchProfile = useCallback(async () => {
    // Don't fetch if user is not ready or auth is still loading
    if (authLoading || !user) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log('Fetching profile for user:', user.uid);
      const data = await apiClient.get<UserProfile>('/user/profile');
      setProfile(data);
      setRetryCount(0); // Reset retry count on success
    } catch (err) {
      const error = err as ApiError;
      console.error('Profile fetch error:', error);
      setError(error.message || 'Failed to fetch profile');
      
      // Auto-retry once if it's an auth error and we haven't retried yet
      if (error.message?.includes('authorization') && retryCount === 0) {
        setRetryCount(1);
        console.log('Auto-retrying profile fetch...');
        setTimeout(() => {
          fetchProfile();
        }, 1000);
      }
    } finally {
      setLoading(false);
    }
  }, [user, authLoading, retryCount]);

  // Fetch profile when user is ready
  useEffect(() => {
    if (!authLoading && user) {
      fetchProfile();
    }
  }, [fetchProfile, user, authLoading]);

  const handleRetry = () => {
    setRetryCount(0);
    fetchProfile();
  };

  return (
    <ProtectedRoute>
      <div className="max-w-2xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Profile</h1>
            <p className="mt-2 text-gray-600">
              Manage your account information
            </p>
          </div>

          {/* Auth Status Debug Info */}
          <Card className="p-4 bg-blue-50">
            <h3 className="text-sm font-medium text-blue-800 mb-2">
              Auth Status:
            </h3>
            <div className="text-xs text-blue-700 space-y-1">
              <p>Auth Loading: {authLoading ? 'Yes' : 'No'}</p>
              <p>User Ready: {user ? 'Yes' : 'No'}</p>
              <p>User Email: {user?.email || 'Not available'}</p>
              <p>Retry Count: {retryCount}</p>
            </div>
          </Card>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex items-start">
                <div className="flex-1">
                  <h3 className="text-sm font-medium text-red-800">
                    Error Loading Profile
                  </h3>
                  <p className="mt-1 text-sm text-red-700">{error}</p>
                </div>
                <Button
                  onClick={handleRetry}
                  size="sm"
                  variant="outline"
                  className="ml-4"
                >
                  Retry
                </Button>
              </div>
            </div>
          )}

          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">Account Details</h2>
              <Button
                onClick={handleRetry}
                loading={loading}
                disabled={loading || authLoading}
                variant="outline"
                size="sm"
              >
                {loading ? <LoadingSpinner size="sm" /> : 'Refresh'}
              </Button>
            </div>

            {/* Show loading state */}
            {(loading || authLoading) && !profile ? (
              <div className="flex flex-col items-center justify-center py-12">
                <LoadingSpinner size="lg" />
                <p className="mt-4 text-sm text-gray-600">
                  {authLoading ? 'Authenticating...' : 'Loading profile...'}
                </p>
              </div>
            ) : profile ? (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Email
                    </label>
                    <p className="mt-1 text-sm text-gray-900">{profile.email}</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Email Verified
                    </label>
                    <div className="mt-1 flex items-center">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        profile.email_verified 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {profile.email_verified ? 'Verified' : 'Not Verified'}
                      </span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Display Name
                    </label>
                    <p className="mt-1 text-sm text-gray-900">
                      {profile.name || 'Not set'}
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      User ID
                    </label>
                    <p className="mt-1 text-sm text-gray-900 font-mono break-all">
                      {profile.uid}
                    </p>
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700">
                      Last Authentication
                    </label>
                    <p className="mt-1 text-sm text-gray-900">
                      {new Date(profile.auth_time * 1000).toLocaleString()}
                    </p>
                  </div>
                </div>

                {profile.picture && (
                  <div className="pt-4 border-t border-gray-200">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Profile Picture
                    </label>
                    <Image
                      src={profile.picture}
                      alt="Profile"
                      width={80}
                      height={80}
                      className="rounded-full object-cover"
                    />
                  </div>
                )}

                {/* Additional Profile Information */}
                {profile.firebase && (
                  <div className="pt-4 border-t border-gray-200">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Firebase Information
                    </label>
                    <div className="bg-gray-50 rounded-md p-3">
                      <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                        {JSON.stringify(profile.firebase, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            ) : !authLoading && user ? (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">No profile data available</p>
                <Button
                  onClick={handleRetry}
                  variant="outline"
                >
                  Try Loading Profile
                </Button>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">Waiting for authentication...</p>
              </div>
            )}
          </Card>

          {/* Profile Actions Card */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Profile Actions</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Button
                onClick={() => window.location.href = '/dashboard'}
                variant="outline"
              >
                Back to Dashboard
              </Button>
              
              <Button
                onClick={() => {
                  alert('Edit profile functionality can be added here');
                }}
                variant="outline"
              >
                Edit Profile
              </Button>
              
              <Button
                onClick={() => {
                  window.location.reload();
                }}
                variant="outline"
              >
                Refresh Session
              </Button>
              
              <Button
                onClick={() => {
                  alert('Account settings functionality can be added here');
                }}
                variant="outline"
              >
                Account Settings
              </Button>
            </div>
          </Card>

          {/* Client-side User Info Card */}
          {user && (
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Client-side User Info</h2>
              <div className="bg-blue-50 rounded-md p-4">
                <h3 className="text-sm font-medium text-blue-800 mb-2">
                  Current User State (from Firebase):
                </h3>
                <pre className="text-xs text-blue-700 whitespace-pre-wrap">
                  {JSON.stringify(user, null, 2)}
                </pre>
              </div>
            </Card>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}