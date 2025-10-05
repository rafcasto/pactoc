import React from 'react';
import { AlertCircle, Clock, Users, Calendar, ExternalLink } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';
import { WorkflowInvitation } from '@/lib/hooks/useDashboard';

interface PriorityTask {
  id: string;
  type: 'urgent_review' | 'expiring_invitation' | 'overdue_followup';
  title: string;
  description: string;
  daysAgo?: number;
  daysUntilExpiry?: number;
  priority: 'high' | 'medium' | 'low';
  action: {
    label: string;
    href: string;
  };
  patient: {
    name: string;
    email: string;
  };
}

interface PriorityQueueProps {
  pendingReviews: WorkflowInvitation[];
  pendingInvitations: WorkflowInvitation[];
  approvedPlans: WorkflowInvitation[];
  loading?: boolean;
}

export const PriorityQueue: React.FC<PriorityQueueProps> = ({
  pendingReviews,
  pendingInvitations,
  approvedPlans,
  loading
}) => {
  const createPriorityTasks = (): PriorityTask[] => {
    const tasks: PriorityTask[] = [];
    const now = new Date();

    // Add urgent reviews (submissions older than 48 hours)
    pendingReviews.forEach(review => {
      if (review.submitted_at) {
        const submittedDate = new Date(review.submitted_at);
        const hoursSinceSubmission = Math.floor((now.getTime() - submittedDate.getTime()) / (1000 * 60 * 60));
        const daysSinceSubmission = Math.floor(hoursSinceSubmission / 24);

        if (hoursSinceSubmission >= 48) {
          tasks.push({
            id: `urgent-review-${review.invitation_id}`,
            type: 'urgent_review',
            title: 'Urgent: Patient Form Review Needed',
            description: `Form submitted ${daysSinceSubmission} day${daysSinceSubmission !== 1 ? 's' : ''} ago`,
            daysAgo: daysSinceSubmission,
            priority: hoursSinceSubmission >= 72 ? 'high' : 'medium',
            action: {
              label: 'Review Now',
              href: `/meal-plan-workflow?review=${review.invitation_id}`
            },
            patient: {
              name: review.patient_name,
              email: review.email
            }
          });
        }
      }
    });

    // Add expiring invitations (expire within 3 days)
    pendingInvitations.forEach(invitation => {
      if (invitation.expires_at) {
        const expiryDate = new Date(invitation.expires_at);
        const hoursUntilExpiry = Math.floor((expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60));
        const daysUntilExpiry = Math.ceil(hoursUntilExpiry / 24);

        if (hoursUntilExpiry > 0 && hoursUntilExpiry <= 72) { // Within 3 days
          tasks.push({
            id: `expiring-${invitation.invitation_id}`,
            type: 'expiring_invitation',
            title: 'Invitation Expiring Soon',
            description: `Expires in ${daysUntilExpiry} day${daysUntilExpiry !== 1 ? 's' : ''}`,
            daysUntilExpiry,
            priority: hoursUntilExpiry <= 24 ? 'high' : 'medium',
            action: {
              label: 'Resend',
              href: `/invitations/${invitation.invitation_id}`
            },
            patient: {
              name: invitation.patient_name,
              email: invitation.email
            }
          });
        }
      }
    });

    // Add overdue follow-ups (approved plans with no recent activity)
    approvedPlans.forEach(plan => {
      if (plan.approved_at && plan.start_date) {
        const approvedDate = new Date(plan.approved_at);
        const startDate = new Date(plan.start_date);
        const daysSinceApproval = Math.floor((now.getTime() - approvedDate.getTime()) / (1000 * 60 * 60 * 24));
        const daysSinceStart = Math.floor((now.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));

        // If plan started more than 7 days ago, suggest follow-up
        if (daysSinceStart >= 7 && daysSinceStart <= 30) {
          tasks.push({
            id: `followup-${plan.meal_plan_id}`,
            type: 'overdue_followup',
            title: 'Follow-up Due',
            description: `Meal plan active for ${daysSinceStart} days`,
            daysAgo: daysSinceStart,
            priority: daysSinceStart >= 14 ? 'medium' : 'low',
            action: {
              label: 'Check Progress',
              href: `/patients/${plan.patient_id}`
            },
            patient: {
              name: plan.patient_name,
              email: plan.email || ''
            }
          });
        }
      }
    });

    // Sort by priority and recency
    return tasks.sort((a, b) => {
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
      if (priorityDiff !== 0) return priorityDiff;

      // Within same priority, sort by urgency
      if (a.daysAgo && b.daysAgo) return b.daysAgo - a.daysAgo;
      if (a.daysUntilExpiry && b.daysUntilExpiry) return a.daysUntilExpiry - b.daysUntilExpiry;
      
      return 0;
    }).slice(0, 5); // Limit to 5 most important tasks
  };

  const getPriorityColor = (priority: PriorityTask['priority']) => {
    switch (priority) {
      case 'high': return 'border-l-red-500 bg-red-50';
      case 'medium': return 'border-l-yellow-500 bg-yellow-50';
      case 'low': return 'border-l-blue-500 bg-blue-50';
    }
  };

  const getPriorityIcon = (type: PriorityTask['type']) => {
    switch (type) {
      case 'urgent_review': return <AlertCircle className="h-4 w-4 text-red-600" />;
      case 'expiring_invitation': return <Clock className="h-4 w-4 text-yellow-600" />;
      case 'overdue_followup': return <Calendar className="h-4 w-4 text-blue-600" />;
    }
  };

  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Priority Queue</h3>
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="animate-pulse">
              <div className="border-l-4 border-gray-200 bg-gray-50 p-4 rounded-r-lg">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                  <div className="h-8 w-20 bg-gray-200 rounded"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  const priorityTasks = createPriorityTasks();

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Priority Queue</h3>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-red-500"></div>
          <span className="text-xs text-gray-500">High</span>
          <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
          <span className="text-xs text-gray-500">Medium</span>
          <div className="w-2 h-2 rounded-full bg-blue-500"></div>
          <span className="text-xs text-gray-500">Low</span>
        </div>
      </div>

      {priorityTasks.length === 0 ? (
        <div className="text-center py-8">
          <Users className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">All caught up!</p>
          <p className="text-sm text-gray-400 mt-1">
            No urgent tasks require your attention
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {priorityTasks.map((task) => (
            <div
              key={task.id}
              className={`border-l-4 p-4 rounded-r-lg ${getPriorityColor(task.priority)}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="flex-shrink-0 mt-0.5">
                    {getPriorityIcon(task.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium text-gray-900">
                      {task.title}
                    </h4>
                    <p className="text-xs text-gray-600 mt-1">
                      {task.patient.name} • {task.description}
                    </p>
                  </div>
                </div>
                <div className="flex-shrink-0 ml-3">
                  <Link href={task.action.href}>
                    <Button variant="outline" size="sm" className="text-xs">
                      {task.action.label}
                      <ExternalLink className="h-3 w-3 ml-1" />
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};
