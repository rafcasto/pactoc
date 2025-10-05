import React from 'react';
import { Plus, Users, FileText, Send, Eye, BarChart3 } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';

interface QuickAction {
  title: string;
  description: string;
  icon: React.ReactNode;
  href: string;
  color: string;
  action?: () => void;
}

interface QuickActionsProps {
  onCreateInvitation?: () => void;
}

export const QuickActions: React.FC<QuickActionsProps> = ({ onCreateInvitation }) => {
  const actions: QuickAction[] = [
    {
      title: 'Send Invitation',
      description: 'Invite a new patient to complete their meal plan',
      icon: <Send className="h-5 w-5" />,
      href: '/meal-plan-workflow',
      color: 'text-blue-600 bg-blue-50 hover:bg-blue-100',
      action: onCreateInvitation,
    },
    {
      title: 'View Patients',
      description: 'Manage and review all your patients',
      icon: <Users className="h-5 w-5" />,
      href: '/patients',
      color: 'text-green-600 bg-green-50 hover:bg-green-100',
    },
    {
      title: 'Manage Recipes',
      description: 'Create and edit recipe templates',
      icon: <FileText className="h-5 w-5" />,
      href: '/recipes',
      color: 'text-purple-600 bg-purple-50 hover:bg-purple-100',
    },
    {
      title: 'View Meal Plans',
      description: 'Review active and completed meal plans',
      icon: <Eye className="h-5 w-5" />,
      href: '/meal-plans',
      color: 'text-indigo-600 bg-indigo-50 hover:bg-indigo-100',
    },
    {
      title: 'Analytics',
      description: 'View performance metrics and insights',
      icon: <BarChart3 className="h-5 w-5" />,
      href: '/analytics',
      color: 'text-orange-600 bg-orange-50 hover:bg-orange-100',
    },
    {
      title: 'Invitations',
      description: 'Manage patient invitations and links',
      icon: <Plus className="h-5 w-5" />,
      href: '/invitations',
      color: 'text-teal-600 bg-teal-50 hover:bg-teal-100',
    },
  ];

  const handleActionClick = (action: QuickAction) => {
    if (action.action) {
      action.action();
    }
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {actions.map((action, index) => (
          <div key={index}>
            {action.action ? (
              <button
                onClick={() => handleActionClick(action)}
                className={`w-full p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-all duration-200 text-left ${action.color}`}
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    {action.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium text-gray-900">
                      {action.title}
                    </h4>
                    <p className="text-xs text-gray-500 mt-1">
                      {action.description}
                    </p>
                  </div>
                </div>
              </button>
            ) : (
              <Link href={action.href}>
                <div className={`w-full p-4 rounded-lg border border-gray-200 hover:border-gray-300 transition-all duration-200 cursor-pointer ${action.color}`}>
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      {action.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-gray-900">
                        {action.title}
                      </h4>
                      <p className="text-xs text-gray-500 mt-1">
                        {action.description}
                      </p>
                    </div>
                  </div>
                </div>
              </Link>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
};
