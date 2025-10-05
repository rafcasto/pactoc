'use client';

import React, { useState, useEffect } from 'react';
import { AuthenticatedLayout } from '@/components/layout/AuthenticatedLayout';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { 
  InvitationTable, 
  CreateInvitationModal, 
  InvitationStats,
  type Invitation 
} from '@/components/invitations';
import { Plus } from 'lucide-react';
import { apiClient } from '@/lib/firebase/api';
// import { useToast } from '@/components/ui/Toast';

// Simple toast fallback for now
const useToast = () => ({
  toast: ({ type, title, message }: { type: string; title: string; message: string }) => {
    if (type === 'success') {
      alert(`✅ ${title}: ${message}`);
    } else if (type === 'error') {
      alert(`❌ ${title}: ${message}`);
    } else {
      alert(`${title}: ${message}`);
    }
  }
});

export default function InvitationsPage() {
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [stats, setStats] = useState<{
    total: number;
    pending: number;
    completed: number;
    expired: number;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [resending, setResending] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [canceling, setCanceling] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadInvitations();
    loadStats();
  }, []);

  const loadInvitations = async () => {
    try {
      setLoading(true);
      console.log('InvitationsPage - Loading invitations...');
      const data = await apiClient.get<{ invitations: Invitation[] }>('/api/invitations');
      console.log('InvitationsPage - Invitations loaded:', data);
      setInvitations(data.invitations || []);
    } catch (error) {
      console.error('InvitationsPage - Error loading invitations:', error);
      toast({
        type: 'error',
        title: 'Error',
        message: 'Failed to load invitations'
      });
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      console.log('InvitationsPage - Loading stats...');
      const data = await apiClient.get<{ stats: any }>('/api/invitations/stats');
      console.log('InvitationsPage - Stats loaded:', data);
      setStats(data.stats);
    } catch (error) {
      console.error('InvitationsPage - Error loading stats:', error);
      // Don't show error toast for stats since it's not critical
    }
  };

  const handleCreateInvitation = async (data: { email: string; first_name?: string; last_name?: string }) => {
    console.log('InvitationsPage - handleCreateInvitation called with data:', data);
    
    try {
      setCreating(true);
      console.log('InvitationsPage - Creating invitation, loading state set to true');
      
      const result = await apiClient.post('/api/invitations', data);
      console.log('InvitationsPage - API success response:', result);
      
      toast({
        type: 'success',
        title: 'Success',
        message: 'Invitation created successfully'
      });
      
      setShowCreateModal(false);
      loadInvitations();
      loadStats();
    } catch (error) {
      console.error('InvitationsPage - Error creating invitation:', error);
      toast({
        type: 'error',
        title: 'Error',
        message: `Failed to create invitation: ${error instanceof Error ? error.message : String(error)}`
      });
    } finally {
      setCreating(false);
      console.log('InvitationsPage - Creating state set back to false');
    }
  };

  const handleCopyLink = async (link: string) => {
    try {
      await navigator.clipboard.writeText(link);
      toast({
        type: 'success',
        title: 'Copied',
        message: 'Invitation link copied to clipboard'
      });
    } catch (error) {
      console.error('Error copying link:', error);
      toast({
        type: 'error',
        title: 'Error',
        message: 'Failed to copy link'
      });
    }
  };

  const handleResend = async (invitationId: string) => {
    try {
      setResending(true);
      await apiClient.post(`/api/invitations/resend/${invitationId}`);
      
      toast({
        type: 'success',
        title: 'Success',
        message: 'Invitation resent successfully'
      });
      
      loadInvitations();
      loadStats();
    } catch (error) {
      console.error('Error resending invitation:', error);
      toast({
        type: 'error',
        title: 'Error',
        message: 'Failed to resend invitation'
      });
    } finally {
      setResending(false);
    }
  };

  const handleRegenerate = async (invitationId: string) => {
    try {
      setRegenerating(true);
      await apiClient.post(`/api/invitations/regenerate/${invitationId}`);
      
      toast({
        type: 'success',
        title: 'Success',
        message: 'Invitation link regenerated successfully'
      });
      
      loadInvitations();
    } catch (error) {
      console.error('Error regenerating invitation:', error);
      toast({
        type: 'error',
        title: 'Error',
        message: 'Failed to regenerate invitation'
      });
    } finally {
      setRegenerating(false);
    }
  };

  const handleCancel = async (invitationId: string) => {
    try {
      setCanceling(true);
      await apiClient.delete(`/api/invitations/${invitationId}`);
      
      toast({
        type: 'success',
        title: 'Success',
        message: 'Invitation cancelled successfully'
      });
      
      loadInvitations();
      loadStats();
    } catch (error) {
      console.error('Error cancelling invitation:', error);
      toast({
        type: 'error',
        title: 'Error',
        message: 'Failed to cancel invitation'
      });
    } finally {
      setCanceling(false);
    }
  };

  return (
    <AuthenticatedLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Patient Invitations</h1>
            <p className="text-gray-600">Manage patient invitations and track their status</p>
          </div>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Create Invitation
          </Button>
        </div>

        <InvitationStats stats={stats || undefined} loading={!stats} />

        <Card>
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">All Invitations</h2>
            <InvitationTable
              invitations={invitations}
              loading={loading}
              onCopyLink={handleCopyLink}
              onResend={handleResend}
              onRegenerate={handleRegenerate}
              onCancel={handleCancel}
              resending={resending}
              regenerating={regenerating}
              canceling={canceling}
              showRegenerateAction={true}
            />
          </div>
        </Card>

        <CreateInvitationModal
          open={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSubmit={handleCreateInvitation}
          loading={creating}
        />
      </div>
    </AuthenticatedLayout>
  );
}
