'use client';

import React, { useState } from 'react';
import { useAuth } from '@/components/auth/AuthProvider';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { apiClient } from '@/lib/firebase/api';

export default function DebugPage() {
  const { user, login, logout } = useAuth();
  const [email, setEmail] = useState('test@example.com');
  const [password, setPassword] = useState('password123');
  const [testResult, setTestResult] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    try {
      setLoading(true);
      await login(email, password);
      setTestResult('✅ Login successful');
    } catch (error) {
      setTestResult(`❌ Login failed: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const testInvitationAPI = async () => {
    try {
      setLoading(true);
      setTestResult('Testing invitation API...');
      
      const result = await apiClient.get('/api/invitations');
      setTestResult(`✅ API call successful: ${JSON.stringify(result, null, 2)}`);
    } catch (error) {
      setTestResult(`❌ API call failed: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const createTestInvitation = async () => {
    try {
      setLoading(true);
      setTestResult('Creating test invitation...');
      
      const result = await apiClient.post('/api/invitations', {
        email: 'testpatient@example.com',
        first_name: 'Test',
        last_name: 'Patient'
      });
      setTestResult(`✅ Invitation created: ${JSON.stringify(result, null, 2)}`);
    } catch (error) {
      setTestResult(`❌ Invitation creation failed: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">🧪 Debug Authentication & API</h1>
      
      <div className="grid gap-6">
        {/* Authentication Status */}
        <Card>
          <div className="p-6">
            <h2 className="text-lg font-semibold mb-4">🔐 Authentication Status</h2>
            {user ? (
              <div className="space-y-2">
                <p className="text-green-600">✅ Logged in as: {user.email}</p>
                <p>UID: {user.uid}</p>
                <Button onClick={logout} variant="outline">
                  Logout
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-red-600">❌ Not logged in</p>
                <div className="space-y-2">
                  <Input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                  <Input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <Button onClick={handleLogin} loading={loading}>
                    Login
                  </Button>
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* API Testing */}
        <Card>
          <div className="p-6">
            <h2 className="text-lg font-semibold mb-4">🌐 API Testing</h2>
            <div className="space-y-4">
              <div className="flex gap-2">
                <Button 
                  onClick={testInvitationAPI} 
                  loading={loading}
                  disabled={!user}
                >
                  Test GET /api/invitations
                </Button>
                <Button 
                  onClick={createTestInvitation} 
                  loading={loading}
                  disabled={!user}
                >
                  Create Test Invitation
                </Button>
              </div>
              
              {testResult && (
                <div className="mt-4 p-4 bg-gray-100 rounded-md">
                  <pre className="text-sm whitespace-pre-wrap">{testResult}</pre>
                </div>
              )}
            </div>
          </div>
        </Card>

        {/* Token Information */}
        <Card>
          <div className="p-6">
            <h2 className="text-lg font-semibold mb-4">🎫 Token Information</h2>
            <div className="space-y-2">
              <p>localStorage token: {typeof window !== 'undefined' && localStorage.getItem('token') ? 'Present' : 'Not found'}</p>
              <p>Current user: {user ? 'Authenticated' : 'Not authenticated'}</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
