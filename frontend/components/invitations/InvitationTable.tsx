'use client';

import React from 'react';
import { DataTable } from '@/components/ui/DataTable';
import { Button } from '@/components/ui/Button';
import { Copy, RefreshCw, Trash2, RotateCw } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

export interface Invitation {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  status: 'pending' | 'completed' | 'expired';
  created_at: string;
  expires_at: string;
  public_link?: string;
}

interface InvitationTableProps {
  invitations: Invitation[];
  loading?: boolean;
  onCopyLink?: (link: string) => void;
  onResend?: (invitationId: string) => void;
  onRegenerate?: (invitationId: string) => void;
  onCancel?: (invitationId: string) => void;
  resending?: boolean;
  regenerating?: boolean;
  canceling?: boolean;
  showRegenerateAction?: boolean;
  onRowClick?: (invitation: Invitation) => void;
}

export function InvitationTable({
  invitations,
  loading = false,
  onCopyLink,
  onResend,
  onRegenerate,
  onCancel,
  resending = false,
  regenerating = false,
  canceling = false,
  showRegenerateAction = false,
  onRowClick
}: InvitationTableProps) {
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
      render: (status: string) => <StatusBadge status={status} />
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
          {record.status === 'pending' && record.public_link && onCopyLink && (
            <Button
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation();
                onCopyLink(record.public_link!);
              }}
              title="Copy invitation link"
            >
              <Copy className="w-4 h-4" />
            </Button>
          )}
          {record.status === 'pending' && onResend && (
            <Button
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation();
                onResend(record.id);
              }}
              loading={resending}
              title="Resend invitation (extend expiry)"
            >
              <RefreshCw className="w-4 h-4" />
            </Button>
          )}
          {record.status === 'pending' && showRegenerateAction && onRegenerate && (
            <Button
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation();
                onRegenerate(record.id);
              }}
              loading={regenerating}
              title="Regenerate invitation link"
            >
              <RotateCw className="w-4 h-4" />
            </Button>
          )}
          {record.status === 'pending' && onCancel && (
            <Button
              size="sm"
              variant="ghost"
              onClick={(e) => {
                e.stopPropagation();
                onCancel(record.id);
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

  return (
    <DataTable
      columns={columns}
      data={invitations}
      loading={loading}
      emptyMessage="No invitations found"
      onRowClick={onRowClick}
    />
  );
}
