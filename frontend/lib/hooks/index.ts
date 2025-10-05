// Re-export all hooks for convenient importing
export { useAuth } from './useAuth';
export { useApi } from './useApi';

// Catalogs hooks
export {
  useMedicalConditions,
  useCreateMedicalCondition,
  useFoodIntolerances,  
  useCreateFoodIntolerance,
  useDietaryPreferences,
  useCreateDietaryPreference,
  useIngredients,
  useCreateIngredient,
  useRecipeTags,
  useCreateRecipeTag,
  useUpdateCatalogItem,
  useDeleteCatalogItem,
  type MedicalCondition,
  type FoodIntolerance,
  type DietaryPreference,
  type Ingredient,
  type RecipeTag
} from './useCatalogs';

// Dashboard hooks
export { 
  useDashboard, 
  type DashboardData, 
  type DashboardStats, 
  type WorkflowInvitation 
} from './useDashboard';

// Invitations hooks  
export {
  useInvitations,
  useInvitationStats,
  useCreateInvitation,
  useResendInvitation,
  useRegenerateInvitation,
  useCancelInvitation,
  type Invitation,
  type CreateInvitationData,
  type InvitationStats
} from './useInvitations';

// Re-export individual hook files that may not have specific exports checked yet
export * from './useInvitationActions';
export * from './useMealPlans'; 
export * from './usePatients';
export * from './useRecaptcha';
export * from './useRecipes';