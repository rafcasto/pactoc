"""
Servicio para generación automática de planes de comidas personalizados.
"""
import random
import secrets
from datetime import datetime, date, timedelta, time
from typing import List, Dict, Any, Optional
from sqlalchemy import and_, not_, exists
from sqlalchemy.orm import joinedload

from app.services.database_service import db
from app.models.sql_models import (
    Patient, MealPlan, MealPlanMeal, MealPlanToken,
    Recipe, RecipeIngredient, Ingredient,
    PatientMedicalCondition, PatientIntolerance, PatientDietaryPreference,
    MedicalCondition, FoodIntolerance, DietaryPreference
)


class MealPlanGeneratorService:
    """Servicio para generar planes de comidas automáticamente."""
    
    def __init__(self):
        self.MEAL_TIMES = {
            'breakfast': time(8, 0),    # 8:00 AM
            'lunch': time(13, 0),       # 1:00 PM
            'dinner': time(19, 0)       # 7:00 PM
        }
        
        self.DAY_ORDER = [
            'monday', 'tuesday', 'wednesday', 'thursday',
            'friday', 'saturday', 'sunday'
        ]
    
    def generate_for_new_patient(self, patient_id: int, generated_by_uid: str) -> Dict[str, Any]:
        """
        Genera un plan de comidas automáticamente para un paciente nuevo.
        
        Args:
            patient_id: ID del paciente
            generated_by_uid: UID del usuario que genera el plan
            
        Returns:
            Dict con el plan generado y token de acceso
        """
        try:
            # 1. Obtener perfil del paciente con restricciones
            patient = self._get_patient_with_restrictions(patient_id)
            if not patient:
                raise ValueError(f"Paciente {patient_id} no encontrado")
            
            # 2. Calcular fechas (siguiente lunes a domingo)
            start_date, end_date = self._get_next_week_dates()
            
            # 3. Filtrar recetas compatibles
            compatible_recipes = self._filter_compatible_recipes(patient)
            
            # 4. Validar que tengamos suficientes recetas
            self._validate_recipe_availability(compatible_recipes)
            
            # 5. Distribuir recetas en la semana
            week_meals = self._distribute_recipes_across_week(compatible_recipes)
            
            # 6. Crear plan en base de datos
            plan = self._create_meal_plan(
                patient_id=patient_id,
                start_date=start_date,
                end_date=end_date,
                generated_by_uid=generated_by_uid
            )
            
            # 7. Crear comidas del plan
            self._create_meal_plan_meals(plan.id, week_meals)
            
            # 8. Generar token para visualización pública
            token = self._generate_meal_plan_token(plan.id)
            
            return {
                'plan': plan,
                'token': token,
                'meal_count': len(week_meals),
                'week_start': start_date.isoformat(),
                'week_end': end_date.isoformat()
            }
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error generando plan de comidas: {str(e)}")
    
    def _get_patient_with_restrictions(self, patient_id: int) -> Optional[Patient]:
        """Obtiene el paciente con todas sus restricciones cargadas."""
        return db.session.query(Patient).options(
            joinedload(Patient.medical_conditions).joinedload(PatientMedicalCondition.condition),
            joinedload(Patient.intolerances).joinedload(PatientIntolerance.intolerance),
            joinedload(Patient.dietary_preferences).joinedload(PatientDietaryPreference.preference)
        ).filter(Patient.id == patient_id).first()
    
    def _get_next_week_dates(self):
        """Calcula las fechas del próximo lunes y domingo."""
        today = datetime.now().date()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:  # Si es lunes, usar la próxima semana
            days_until_monday = 7
        
        start_date = today + timedelta(days=days_until_monday)
        end_date = start_date + timedelta(days=6)
        
        return start_date, end_date
    
    def _filter_compatible_recipes(self, patient: Patient) -> Dict[str, List[Recipe]]:
        """
        Filtra recetas compatibles con las restricciones del paciente.
        
        Args:
            patient: Paciente con restricciones cargadas
            
        Returns:
            Dict con recetas por tipo de comida
        """
        # Obtener ingredientes restringidos
        restricted_ingredients = self._get_restricted_ingredients(patient)
        
        # Construir query base para recetas activas
        base_query = db.session.query(Recipe).filter(Recipe.is_active == True)
        
        # Excluir recetas que contengan ingredientes restringidos
        if restricted_ingredients:
            base_query = base_query.filter(
                not_(exists().where(
                    and_(
                        RecipeIngredient.recipe_id == Recipe.id,
                        RecipeIngredient.ingredient_id.in_(restricted_ingredients)
                    )
                ))
            )
        
        # Obtener todas las recetas compatibles
        all_recipes = base_query.all()
        
        # Agrupar por tipo de comida
        grouped_recipes = {
            'breakfast': [r for r in all_recipes if r.meal_type == 'breakfast'],
            'lunch': [r for r in all_recipes if r.meal_type == 'lunch'],
            'dinner': [r for r in all_recipes if r.meal_type == 'dinner']
        }
        
        return grouped_recipes
    
    def _get_restricted_ingredients(self, patient: Patient) -> List[int]:
        """
        Obtiene los IDs de ingredientes que el paciente no puede consumir.
        
        Args:
            patient: Paciente con restricciones
            
        Returns:
            Lista de IDs de ingredientes restringidos
        """
        restricted_ingredients = []
        
        # Mapeo de intolerancias a ingredientes restringidos
        intolerance_mappings = {
            'Lactosa': ['leche', 'queso', 'yogur', 'mantequilla', 'crema'],
            'Gluten': ['harina de trigo', 'avena', 'cebada', 'centeno'],
            'Nueces': ['nueces', 'almendras', 'pistachos', 'avellanas'],
            'Mariscos': ['camarones', 'langosta', 'cangrejo', 'mejillones'],
            'Huevo': ['huevo', 'clara de huevo', 'yema de huevo'],
            'Soya': ['salsa de soya', 'tofu', 'tempeh', 'leche de soya']
        }
        
        # Obtener ingredientes basados en intolerancias
        for intolerance_rel in patient.intolerances:
            intolerance_name = intolerance_rel.intolerance.intolerance_name
            if intolerance_name in intolerance_mappings:
                ingredient_names = intolerance_mappings[intolerance_name]
                ingredients = db.session.query(Ingredient.id).filter(
                    Ingredient.ingredient_name.in_(ingredient_names)
                ).all()
                restricted_ingredients.extend([ing.id for ing in ingredients])
        
        # TODO: Agregar restricciones basadas en condiciones médicas si es necesario
        # Por ejemplo: diabéticos evitar azúcar, hipertensos evitar sal, etc.
        
        return list(set(restricted_ingredients))  # Eliminar duplicados
    
    def _validate_recipe_availability(self, compatible_recipes: Dict[str, List[Recipe]]):
        """Valida que tengamos suficientes recetas para generar un plan semanal."""
        required_per_type = 7  # 7 días de la semana
        
        for meal_type, recipes in compatible_recipes.items():
            if len(recipes) < required_per_type:
                raise ValueError(
                    f"No hay suficientes recetas de {meal_type}. "
                    f"Se necesitan {required_per_type}, solo hay {len(recipes)}"
                )
    
    def _distribute_recipes_across_week(self, compatible_recipes: Dict[str, List[Recipe]]) -> List[Dict]:
        """
        Distribuye las recetas compatibles a lo largo de la semana.
        
        Args:
            compatible_recipes: Recetas agrupadas por tipo
            
        Returns:
            Lista de comidas para la semana
        """
        week_meals = []
        
        # Barajar recetas para mayor variedad
        breakfast_recipes = self._shuffle_recipes(compatible_recipes['breakfast'])
        lunch_recipes = self._shuffle_recipes(compatible_recipes['lunch'])
        dinner_recipes = self._shuffle_recipes(compatible_recipes['dinner'])
        
        # Asignar recetas a cada día
        for day_index, day_name in enumerate(self.DAY_ORDER):
            # Desayuno
            week_meals.append({
                'day_of_week': day_name,
                'meal_type': 'breakfast',
                'recipe_id': breakfast_recipes[day_index].id,
                'scheduled_time': self.MEAL_TIMES['breakfast'],
                'servings': 1.0
            })
            
            # Almuerzo
            week_meals.append({
                'day_of_week': day_name,
                'meal_type': 'lunch',
                'recipe_id': lunch_recipes[day_index].id,
                'scheduled_time': self.MEAL_TIMES['lunch'],
                'servings': 1.0
            })
            
            # Cena
            week_meals.append({
                'day_of_week': day_name,
                'meal_type': 'dinner',
                'recipe_id': dinner_recipes[day_index].id,
                'scheduled_time': self.MEAL_TIMES['dinner'],
                'servings': 1.0
            })
        
        return week_meals
    
    def _shuffle_recipes(self, recipes: List[Recipe]) -> List[Recipe]:
        """Baraja las recetas para mayor variedad."""
        shuffled = recipes.copy()
        random.shuffle(shuffled)
        return shuffled
    
    def _create_meal_plan(self, patient_id: int, start_date, end_date, generated_by_uid: str) -> MealPlan:
        """Crea el registro del plan de comidas."""
        plan = MealPlan(
            patient_id=patient_id,
            plan_name=f"Plan Semanal - {start_date.strftime('%d/%m/%Y')}",
            start_date=start_date,
            end_date=end_date,
            status='approved',  # Auto-aprobado ya que es generado automáticamente
            notes="Plan generado automáticamente al completar perfil",
            generated_by_uid=generated_by_uid,
            approved_by_uid=generated_by_uid,  # Auto-aprobado
            approved_at=datetime.utcnow()
        )
        
        db.session.add(plan)
        db.session.commit()
        
        return plan
    
    def _create_meal_plan_meals(self, plan_id: int, week_meals: List[Dict]):
        """Crea las comidas individuales del plan."""
        meal_objects = []
        
        for meal_data in week_meals:
            meal = MealPlanMeal(
                plan_id=plan_id,
                recipe_id=meal_data['recipe_id'],
                day_of_week=meal_data['day_of_week'],
                meal_type=meal_data['meal_type'],
                scheduled_time=meal_data['scheduled_time'],
                servings=meal_data['servings']
            )
            meal_objects.append(meal)
        
        db.session.add_all(meal_objects)
        db.session.commit()
    
    def _generate_meal_plan_token(self, plan_id: int) -> str:
        """Genera un token para acceso público al plan de comidas."""
        token = MealPlanToken(
            plan_id=plan_id,
            expires_at=None  # Los tokens de planes no expiran
        )
        
        db.session.add(token)
        db.session.commit()
        
        return token.token
    
    def get_plan_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un plan de comidas por su token público.
        
        Args:
            token: Token de acceso público
            
        Returns:
            Dict con el plan y datos del paciente o None si no existe
        """
        token_obj = db.session.query(MealPlanToken).filter(
            MealPlanToken.token == token
        ).first()
        
        if not token_obj or not token_obj.is_valid:
            return None
        
        # Obtener plan con todas las relaciones
        plan = db.session.query(MealPlan).options(
            joinedload(MealPlan.patient).joinedload(Patient.medical_conditions).joinedload(PatientMedicalCondition.condition),
            joinedload(MealPlan.patient).joinedload(Patient.intolerances).joinedload(PatientIntolerance.intolerance),
            joinedload(MealPlan.meals).joinedload(MealPlanMeal.recipe).joinedload(Recipe.ingredients).joinedload(RecipeIngredient.ingredient)
        ).filter(MealPlan.id == token_obj.plan_id).first()
        
        if not plan:
            return None
        
        return self._format_plan_for_public_view(plan)
    
    def _format_plan_for_public_view(self, plan: MealPlan) -> Dict[str, Any]:
        """Formatea el plan para la vista pública del paciente."""
        patient = plan.patient
        
        # Agrupar comidas por día
        meals_by_day = {}
        for meal in plan.meals:
            day_name = meal.day_of_week
            if day_name not in meals_by_day:
                meals_by_day[day_name] = []
            
            # Formatear la receta con información completa
            recipe_data = self._format_recipe_for_view(meal.recipe)
            
            meals_by_day[day_name].append({
                'type': meal.meal_type.title(),
                'time': meal.scheduled_time.strftime('%H:%M') if meal.scheduled_time else None,
                'servings': float(meal.servings),
                'recipe': recipe_data
            })
        
        # Ordenar días de la semana
        ordered_meals = []
        day_names_spanish = {
            'monday': 'Lunes',
            'tuesday': 'Martes', 
            'wednesday': 'Miércoles',
            'thursday': 'Jueves',
            'friday': 'Viernes',
            'saturday': 'Sábado',
            'sunday': 'Domingo'
        }
        
        for day_key in self.DAY_ORDER:
            if day_key in meals_by_day:
                ordered_meals.append({
                    'day': day_names_spanish[day_key],
                    'day_of_week': day_key,
                    'meals': sorted(meals_by_day[day_key], key=lambda x: x['time'] or '00:00')
                })
        
        return {
            'patient': {
                'first_name': patient.first_name,
                'conditions': [mc.condition.condition_name for mc in patient.medical_conditions],
                'intolerances': [pi.intolerance.intolerance_name for pi in patient.intolerances]
            },
            'meal_plan': {
                'plan_id': plan.id,
                'plan_name': plan.plan_name,
                'start_date': plan.start_date.isoformat(),
                'end_date': plan.end_date.isoformat(),
                'meals': ordered_meals
            }
        }
    
    def _format_recipe_for_view(self, recipe: Recipe) -> Dict[str, Any]:
        """Formatea una receta para la vista pública."""
        # Generar tags basados en las características de la receta
        tags = []
        
        # Tags nutricionales básicos
        if recipe.total_calories and recipe.total_calories < 300:
            tags.append("Bajo en Calorías")
        if recipe.total_protein and recipe.total_protein > 15:
            tags.append("Alto en Proteína")
        if recipe.total_fiber and recipe.total_fiber > 5:
            tags.append("Rico en Fibra")
        
        # Tags por defecto según tipo de comida
        if recipe.meal_type == 'breakfast':
            tags.append("Energético")
        elif recipe.meal_type == 'lunch':
            tags.append("Nutritivo")
        elif recipe.meal_type == 'dinner':
            tags.append("Ligero")
        
        # Formatear ingredientes
        ingredients = []
        for ri in recipe.ingredients:
            if ri.ingredient:
                quantity_str = f"{ri.quantity:.1f}".rstrip('0').rstrip('.')
                ingredients.append(f"{quantity_str} {ri.unit} de {ri.ingredient.ingredient_name}")
        
        # Formatear instrucciones (dividir por saltos de línea si es texto largo)
        instructions = []
        if recipe.instructions:
            # Si las instrucciones están numeradas, mantener formato
            if any(line.strip().startswith(('1.', '2.', '3.')) for line in recipe.instructions.split('\n')):
                instructions = [line.strip() for line in recipe.instructions.split('\n') if line.strip()]
            else:
                # Si no, crear pasos numerados básicos
                instruction_text = recipe.instructions.strip()
                if len(instruction_text) > 100:
                    # Dividir en pasos lógicos por puntos
                    sentences = instruction_text.split('. ')
                    instructions = [f"{i+1}. {sentence.strip()}{'.' if not sentence.endswith('.') else ''}" 
                                  for i, sentence in enumerate(sentences) if sentence.strip()]
                else:
                    instructions = [f"1. {instruction_text}"]
        
        return {
            'recipe_name': recipe.recipe_name,
            'description': recipe.description,
            'calories': int(recipe.total_calories) if recipe.total_calories else 0,
            'protein': int(recipe.total_protein) if recipe.total_protein else 0,
            'carbs': int(recipe.total_carbs) if recipe.total_carbs else 0,
            'fiber': int(recipe.total_fiber) if recipe.total_fiber else 0,
            'preparation_time': recipe.preparation_time,
            'cooking_time': recipe.cooking_time,
            'difficulty_level': recipe.difficulty_level,
            'tags': tags,
            'ingredients': ingredients,
            'instructions': instructions,
            'image_url': recipe.image_url
        }


# Instancia global del servicio
meal_plan_generator = MealPlanGeneratorService()
