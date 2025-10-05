import React from 'react';
import { cn } from '@/lib/utils/helpers';

interface Badge {
  label: string;
  value: number;
  unit?: string;
  color?: string;
}

interface NutritionBadgeProps {
  nutrition: {
    total_calories?: number;
    total_protein?: number;
    total_carbs?: number;
    total_fat?: number;
    total_fiber?: number;
  };
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function NutritionBadge({ 
  nutrition, 
  className,
  size = 'md' 
}: NutritionBadgeProps) {
  const badges: Badge[] = [
    {
      label: 'Cal',
      value: nutrition.total_calories || 0,
      unit: '',
      color: 'bg-red-100 text-red-800'
    },
    {
      label: 'Prot',
      value: nutrition.total_protein || 0,
      unit: 'g',
      color: 'bg-blue-100 text-blue-800'
    },
    {
      label: 'Carb',
      value: nutrition.total_carbs || 0,
      unit: 'g',
      color: 'bg-yellow-100 text-yellow-800'
    },
    {
      label: 'Fat',
      value: nutrition.total_fat || 0,
      unit: 'g',
      color: 'bg-purple-100 text-purple-800'
    },
    {
      label: 'Fib',
      value: nutrition.total_fiber || 0,
      unit: 'g',
      color: 'bg-green-100 text-green-800'
    }
  ];

  const sizeClasses = {
    sm: 'text-xs px-1.5 py-0.5',
    md: 'text-xs px-2 py-1',
    lg: 'text-sm px-2.5 py-1.5'
  };

  const gapClasses = {
    sm: 'gap-1',
    md: 'gap-1.5',
    lg: 'gap-2'
  };

  return (
    <div className={cn(`flex flex-wrap ${gapClasses[size]}`, className)}>
      {badges.map((badge) => (
        <span
          key={badge.label}
          className={cn(
            `inline-flex items-center rounded-full font-medium ${sizeClasses[size]}`,
            badge.color
          )}
        >
          {badge.label}: {Math.round(badge.value * 100) / 100}{badge.unit}
        </span>
      ))}
    </div>
  );
}

interface DetailedNutritionProps {
  nutrition: {
    total_calories?: number;
    total_protein?: number;
    total_carbs?: number;
    total_fat?: number;
    total_fiber?: number;
  };
  servings?: number;
  className?: string;
}

export function DetailedNutrition({ 
  nutrition, 
  servings = 1,
  className 
}: DetailedNutritionProps) {
  const calculatePerServing = (value: number) => {
    return Math.round((value / servings) * 100) / 100;
  };

  const nutritionItems = [
    {
      label: 'Calorías',
      value: nutrition.total_calories || 0,
      unit: 'kcal',
      color: 'text-red-600',
      bgColor: 'bg-red-50'
    },
    {
      label: 'Proteínas',
      value: nutrition.total_protein || 0,
      unit: 'g',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      label: 'Carbohidratos',
      value: nutrition.total_carbs || 0,
      unit: 'g',
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50'
    },
    {
      label: 'Grasas',
      value: nutrition.total_fat || 0,
      unit: 'g',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
    {
      label: 'Fibra',
      value: nutrition.total_fiber || 0,
      unit: 'g',
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    }
  ];

  return (
    <div className={cn("grid grid-cols-2 md:grid-cols-5 gap-3", className)}>
      {nutritionItems.map((item) => (
        <div
          key={item.label}
          className={cn("p-3 rounded-lg text-center", item.bgColor)}
        >
          <div className={cn("text-lg font-bold", item.color)}>
            {calculatePerServing(item.value)}
            <span className="text-sm font-normal">{item.unit}</span>
          </div>
          <div className="text-xs text-gray-600 mt-1">
            {item.label}
          </div>
          {servings > 1 && (
            <div className="text-xs text-gray-500">
              por porción
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
