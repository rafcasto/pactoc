'use client';

import React from 'react';
import { Card } from '@/components/ui/Card';
import { Mail, Clock, CheckCircle, XCircle } from 'lucide-react';

interface InvitationStatsProps {
  stats?: {
    total: number;
    pending: number;
    completed: number;
    expired: number;
  };
  loading?: boolean;
}

export function InvitationStats({ stats, loading }: InvitationStatsProps) {
  if (loading || !stats) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="p-4 animate-pulse">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-gray-200 rounded mr-3"></div>
              <div>
                <div className="w-8 h-6 bg-gray-200 rounded mb-1"></div>
                <div className="w-16 h-4 bg-gray-200 rounded"></div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card className="p-4">
        <div className="flex items-center">
          <Mail className="w-5 h-5 text-blue-500 mr-3" />
          <div>
            <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
            <div className="text-sm text-gray-500">Total Invitations</div>
          </div>
        </div>
      </Card>
      <Card className="p-4">
        <div className="flex items-center">
          <Clock className="w-5 h-5 text-yellow-500 mr-3" />
          <div>
            <div className="text-2xl font-bold text-yellow-600">{stats.pending}</div>
            <div className="text-sm text-gray-500">Pending</div>
          </div>
        </div>
      </Card>
      <Card className="p-4">
        <div className="flex items-center">
          <CheckCircle className="w-5 h-5 text-green-500 mr-3" />
          <div>
            <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
            <div className="text-sm text-gray-500">Completed</div>
          </div>
        </div>
      </Card>
      <Card className="p-4">
        <div className="flex items-center">
          <XCircle className="w-5 h-5 text-red-500 mr-3" />
          <div>
            <div className="text-2xl font-bold text-red-600">{stats.expired}</div>
            <div className="text-sm text-gray-500">Expired</div>
          </div>
        </div>
      </Card>
    </div>
  );
}
