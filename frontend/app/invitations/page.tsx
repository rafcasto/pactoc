'use client';

import React, { useState } from 'react';
import { AuthenticatedLayout } from '@/components/layout/AuthenticatedLayout';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { DataTable } from '@/components/ui/DataTable';
import { Modal, ModalFooter } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { useInvitations, useInvitationStats, useCreateInvitation, useResendInvitation, useCancelInvitation, type Invitation } from '@/lib/hooks/useInvitations';
import { Copy, Mail, Plus, RefreshCw, Trash2, AlertCircle } from 'lucide-react';

export default function InvitationsPage() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [copiedLink, setCopiedLink] = useState<string | null>(null);

  // Hooks
  const { data: invitationsData, loading, error, refetch } = useInvitations(selectedStatus);
  const { data: statsData } = useInvitationStats();
  const { createInvitation, loading: creating } = useCreateInvitation();
  const { resendInvitation, loading: resending } = useResendInvitation();
  const { cancelInvitation, loading: canceling } = useCancelInvitation();

  const invitations = invitationsData?.invitations || [];
  const stats = statsData?.stats;

  const handleCreateInvitation = async (data: { email: string; first_name?: string; last_name?: string }) => {
    try {
      await createInvitation(data);
      setShowCreateModal(false);
      refetch();
    } catch (error) {
      console.error('Failed to create invitation:', error);
    }
  };

  const handleResendInvitation = async (invitationId: string) => {
    try {
      await resendInvitation(invitationId);
      refetch();
    } catch (error) {
      console.error('Failed to resend invitation:', error);
    }
  };

  const handleCancelInvitation = async (invitationId: string) => {
    if (confirm('Are you sure you want to cancel this invitation?')) {
      try {
        await cancelInvitation(invitationId);
        refetch();
      } catch (error) {
        console.error('Failed to cancel invitation:', error);
      }
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedLink(text);
      setTimeout(() => setCopiedLink(null), 2000);
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
    }
  };

  const getStatusBadge = (status: string) => {
    const baseClasses = "px-2 py-1 text-xs font-medium rounded-full";
    switch (status) {
      case 'pending':
        return <span className={`${baseClasses} bg-yellow-100 text-yellow-800`}>Pending</span>;
      case 'completed':
        return <span className={`${baseClasses} bg-green-100 text-green-800`}>Completed</span>;
      case 'expired':
        return <span className={`${baseClasses} bg-red-100 text-red-800`}>Expired</span>;
      default:
        return <span className={`${baseClasses} bg-gray-100 text-gray-800`}>{status}</span>;
    }
  };

  const columns = [
    {
      key: 'email',
      title: 'Email',
      render: (email: string, record: Invitation) => (
        <div>
          <div className="font-medium">{email}</div>
          {(record.first_name || record.last_name) && (
            <div className="text-sm text-gray-500">
              {record.first_name} {record.last_name}
            </div>
          )}
        </div>
      )
    },
    {
      key: 'status',
      title: 'Status',
      render: (status: string) => getStatusBadge(status)
    },
    {
      key: 'created_at',
      title: 'Created',
      render: (date: string) => new Date(date).toLocaleDateString()
    },
    {
      key: 'expires_at',
      title: 'Expires',
      render: (date: string) => new Date(date).toLocaleDateString()
    },
    {
      key: 'actions',
      title: 'Actions',
      render: (_: any, record: Invitation) => (
        <div className="flex space-x-2">
          {record.status === 'pending' && record.public_link && (
            <Button
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation();
                copyToClipboard(record.public_link!);
              }}
              title="Copy invitation link"
            >
              <Copy className="w-4 h-4" />
            </Button>
          )}
          {record.status === 'pending' && (
            <Button
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation();
                handleResendInvitation(record.id);
              }}
              loading={resending}
              title="Resend invitation"
            >
              <RefreshCw className="w-4 h-4" />
            </Button>
          )}
          {record.status === 'pending' && (
            <Button
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation();
                handleCancelInvitation(record.id);
              }}
              loading={canceling}
              title="Cancel invitation"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          )}
        </div>
      )
    }
  ];

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error loading invitations</h3>
          <p className="text-gray-500 mb-4">{error}</p>
          <Button onClick={refetch}>Try Again</Button>
        </div>
      </div>
    );
  }

  return (
    <AuthenticatedLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Patient Invitations</h1>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Invitation
          </Button>
        </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-4">
            <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
            <div className="text-sm text-gray-500">Total Invitations</div>
          </Card>
          <Card className="p-4">
            <div className="text-2xl font-bold text-yellow-600">{stats.pending}</div>
            <div className="text-sm text-gray-500">Pending</div>
          </Card>
          <Card className="p-4">
            <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
            <div className="text-sm text-gray-500">Completed</div>
          </Card>
          <Card className="p-4">
            <div className="text-2xl font-bold text-red-600">{stats.expired}</div>
            <div className="text-sm text-gray-500">Expired</div>
          </Card>
        </div>
      )}

      {/* Filters */}
      <div className="flex space-x-4">
        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          className="border border-gray-300 rounded-md px-3 py-2 text-sm"
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="completed">Completed</option>
          <option value="expired">Expired</option>
        </select>
      </div>

      {/* Invitations Table */}
      <Card>
        <DataTable
          columns={columns}
          data={invitations}
          loading={loading}
          emptyMessage="No invitations found"
        />
      </Card>

      {/* Copy success notification */}
      {copiedLink && (
        <div className="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-md shadow-lg">
          Invitation link copied to clipboard!
        </div>
      )}

      {/* Create Invitation Modal */}
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

interface CreateInvitationModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: { email: string; first_name?: string; last_name?: string }) => void;
  loading: boolean;
}

function CreateInvitationModal({ open, onClose, onSubmit, loading }: CreateInvitationModalProps) {
  const [formData, setFormData] = useState({
    email: '',
    first_name: '',
    last_name: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.email) return;

    const submitData: any = { email: formData.email };
    if (formData.first_name) submitData.first_name = formData.first_name;
    if (formData.last_name) submitData.last_name = formData.last_name;

    onSubmit(submitData);
  };

  const resetForm = () => {
    setFormData({ email: '', first_name: '', last_name: '' });
  };

  return (
    <Modal
      open={open}
      onClose={() => {
        onClose();
        resetForm();
      }}
      title="Create Patient Invitation"
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email Address *
          </label>
          <Input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
            placeholder="patient@example.com"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              First Name
            </label>
            <Input
              type="text"
              value={formData.first_name}
              onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              placeholder="John"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Last Name
            </label>
            <Input
              type="text"
              value={formData.last_name}
              onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
              placeholder="Doe"
            />
          </div>
        </div>

        <ModalFooter>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={loading} disabled={!formData.email}>
            Create Invitation
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
