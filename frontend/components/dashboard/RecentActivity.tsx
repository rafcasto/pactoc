import React from 'react';
import { Clock, CheckCircle, UserPlus, Send, Calendar } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';
import { WorkflowInvitation } from '@/lib/hooks/useDashboard';

interface RecentActivityProps {
  pendingReviews: WorkflowInvitation[];
  recentApprovals: WorkflowInvitation[];
  pendingInvitations: WorkflowInvitation[];
  loading?: boolean;
}

interface ActivityItem {
  id: string;
  type: 'pending_review' | 'approved' | 'invitation_sent';
  title: string;
  subtitle: string;
  time: string;
  icon: React.ReactNode;
  color: string;
  action?: {
    label: string;
    href?: string;
    onClick?: () => void;
  };
}

export const RecentActivity: React.FC<RecentActivityProps> = ({
  pendingReviews,
  recentApprovals,
  pendingInvitations,
  loading
}) => {
  const formatTimeAgo = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    
    const diffInWeeks = Math.floor(diffInDays / 7);
    return `${diffInWeeks}w ago`;
  };

  const createActivityItems = (): ActivityItem[] => {
    const items: ActivityItem[] = [];

    // Add pending reviews (highest priority)
    pendingReviews.forEach(review => {
      if (review.submitted_at) {
        items.push({
          id: `review-${review.invitation_id}`,
          type: 'pending_review',
          title: `${review.patient_name} - Form Submitted`,
          subtitle: 'Needs meal plan review and approval',
          time: formatTimeAgo(review.submitted_at),
          icon: <Clock className="h-4 w-4" />,
          color: 'text-yellow-600 bg-yellow-50',
          action: {
            label: 'Review',
            href: `/meal-plan-workflow?review=${review.invitation_id}`
          }
        });
      }
    });

    // Add recent approvals
    recentApprovals.slice(0, 3).forEach(approval => {
      if (approval.approved_at) {
        items.push({
          id: `approved-${approval.meal_plan_id}`,
          type: 'approved',
          title: `${approval.patient_name} - Meal Plan Approved`,
          subtitle: `Plan: ${approval.plan_name}`,
          time: formatTimeAgo(approval.approved_at),
          icon: <CheckCircle className="h-4 w-4" />,
          color: 'text-green-600 bg-green-50',
          action: {
            label: 'View',
            href: `/meal-plans/${approval.meal_plan_id}`
          }
        });
      }
    });

    // Add recent invitations
    pendingInvitations.slice(0, 2).forEach(invitation => {
      if (invitation.sent_at) {
        items.push({
          id: `invitation-${invitation.invitation_id}`,
          type: 'invitation_sent',
          title: `Invitation Sent - ${invitation.patient_name}`,
          subtitle: `To: ${invitation.email}`,
          time: formatTimeAgo(invitation.sent_at),
          icon: <Send className="h-4 w-4" />,
          color: 'text-blue-600 bg-blue-50',
          action: {
            label: 'Resend',
            href: `/invitations/${invitation.invitation_id}`
          }
        });
      }
    });

    // Sort by most recent first
    return items.sort((a, b) => {
      // Prioritize pending reviews
      if (a.type === 'pending_review' && b.type !== 'pending_review') return -1;
      if (b.type === 'pending_review' && a.type !== 'pending_review') return 1;
      
      return 0; // Keep original order for same types
    }).slice(0, 8); // Limit to 8 items
  };

  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-4">
          {Array.from({ length: 5 }).map((_, index) => (
            <div key={index} className="animate-pulse">
              <div className="flex items-center space-x-3">
                <div className="h-8 w-8 bg-gray-200 rounded-full"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
                <div className="h-8 w-16 bg-gray-200 rounded"></div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  const activityItems = createActivityItems();

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
        <Link href="/meal-plan-workflow">
          <Button variant="ghost" size="sm">
            View All
          </Button>
        </Link>
      </div>
      
      {activityItems.length === 0 ? (
        <div className="text-center py-8">
          <Calendar className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No recent activity</p>
          <p className="text-sm text-gray-400 mt-1">
            Send an invitation to get started
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {activityItems.map((item) => (
            <div key={item.id} className="flex items-center space-x-3 py-2">
              <div className={`p-2 rounded-full ${item.color}`}>
                {item.icon}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {item.title}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {item.subtitle}
                </p>
              </div>
              <div className="flex items-center space-x-2 text-xs text-gray-400">
                <span>{item.time}</span>
                {item.action && (
                  <Link href={item.action.href || '#'}>
                    <Button variant="ghost" size="sm" className="h-6 px-2 text-xs">
                      {item.action.label}
                    </Button>
                  </Link>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};
