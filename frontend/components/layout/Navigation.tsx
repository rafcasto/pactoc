'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils/helpers';
import { 
  Home, 
  Mail, 
  Users, 
  ChefHat, 
  Calendar, 
  Settings,
  Package
} from 'lucide-react';

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  description?: string;
}

const navigation: NavigationItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: Home,
    description: 'Patient invitations & overview'
  },
  {
    name: 'Patients',
    href: '/patients',
    icon: Users,
    description: 'Manage patients'
  },
  {
    name: 'Recipes',
    href: '/recipes',
    icon: ChefHat,
    description: 'Recipe management'
  },
  {
    name: 'Meal Plans',
    href: '/meal-plans',
    icon: Calendar,
    description: 'Meal planning'
  },
  {
    name: 'Catalogs',
    href: '/catalogs',
    icon: Package,
    description: 'System catalogs'
  }
];

export function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="bg-gray-50 border-r border-gray-200 w-64 min-h-screen">
      <div className="p-4">
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900">Meal Plan System</h2>
          <p className="text-sm text-gray-500">Nutrition Management</p>
        </div>
        
        <ul className="space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
            
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={cn(
                    'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                    isActive
                      ? 'bg-blue-100 text-blue-700 border-r-2 border-blue-500'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  )}
                >
                  <Icon
                    className={cn(
                      'mr-3 h-5 w-5 flex-shrink-0',
                      isActive ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                    )}
                  />
                  <div className="flex-1">
                    <div>{item.name}</div>
                    {item.description && (
                      <div className="text-xs text-gray-500 mt-0.5">
                        {item.description}
                      </div>
                    )}
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </nav>
  );
}
