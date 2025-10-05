import React from 'react';
import { Users, FileText, Clock, CheckCircle, TrendingUp, UserPlus } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import type { DashboardStats as DashboardStatsType } from '@/lib/hooks/useDashboard';

interface StatsCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
}

const StatsCard: React.FC<StatsCardProps> = ({ 
  title, 
  value, 
  icon, 
  color, 
  change, 
  changeType = 'neutral' 
}) => {
  const getChangeColor = () => {
    switch (changeType) {
      case 'positive': return 'text-green-600';
      case 'negative': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {change && (
            <p className={`text-xs ${getChangeColor()} mt-1`}>
              {change}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-full ${color}`}>
          {icon}
        </div>
      </div>
    </Card>
  );
};

interface DashboardStatsProps {
  stats: DashboardStatsType;
  loading?: boolean;
}

export const DashboardStats: React.FC<DashboardStatsProps> = ({ stats, loading }) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
        {Array.from({ length: 6 }).map((_, index) => (
          <Card key={index} className="p-6">
            <div className="animate-pulse">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-8 bg-gray-200 rounded w-1/2"></div>
                </div>
                <div className="h-12 w-12 bg-gray-200 rounded-full"></div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    );
  }

  const statsConfig = [
    {
      title: 'Total Patients',
      value: stats.total_patients,
      icon: <Users className="h-6 w-6 text-blue-600" />,
      color: 'bg-blue-100',
    },
    {
      title: 'Active Meal Plans',
      value: stats.active_meal_plans,
      icon: <FileText className="h-6 w-6 text-green-600" />,
      color: 'bg-green-100',
    },
    {
      title: 'Pending Reviews',
      value: stats.pending_reviews,
      icon: <Clock className="h-6 w-6 text-yellow-600" />,
      color: 'bg-yellow-100',
    },
    {
      title: 'Pending Invitations',
      value: stats.pending_invitations,
      icon: <UserPlus className="h-6 w-6 text-purple-600" />,
      color: 'bg-purple-100',
    },
    {
      title: 'This Week Approvals',
      value: stats.this_week_approvals,
      icon: <CheckCircle className="h-6 w-6 text-emerald-600" />,
      color: 'bg-emerald-100',
      change: 'This week',
      changeType: 'positive' as const,
    },
    {
      title: 'New Patients (Month)',
      value: stats.this_month_new_patients,
      icon: <TrendingUp className="h-6 w-6 text-indigo-600" />,
      color: 'bg-indigo-100',
      change: 'This month',
      changeType: 'positive' as const,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
      {statsConfig.map((stat, index) => (
        <StatsCard
          key={index}
          title={stat.title}
          value={stat.value}
          icon={stat.icon}
          color={stat.color}
          change={stat.change}
          changeType={stat.changeType}
        />
      ))}
    </div>
  );
};
