'use client';

import React from 'react';

interface StatusBadgeProps {
  status: string;
  type?: 'invitation' | 'patient';
}

export function StatusBadge({ status, type = 'invitation' }: StatusBadgeProps) {
  const baseClasses = "px-2 py-1 text-xs font-medium rounded-full";
  
  if (type === 'invitation') {
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
  }
  
  if (type === 'patient') {
    switch (status) {
      case 'pending_review':
        return <span className={`${baseClasses} bg-yellow-100 text-yellow-800`}>Pending Review</span>;
      case 'approved':
        return <span className={`${baseClasses} bg-green-100 text-green-800`}>Approved</span>;
      default:
        return <span className={`${baseClasses} bg-gray-100 text-gray-800`}>{status}</span>;
    }
  }
  
  return <span className={`${baseClasses} bg-gray-100 text-gray-800`}>{status}</span>;
}
