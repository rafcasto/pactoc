"""
Datos de ejemplo para el sistema de recetas dietéticas.
"""
from app.services.database_service import db
from app.models.sql_models import (
    MedicalCondition, FoodIntolerance, DietaryPreference,
    Ingredient, Recipe, RecipeIngredient, RecipeTag, RecipeTagAssignment
)
from decimal import Decimal

def seed_all_data():
    """Sembrar todos los datos de ejemplo."""
    try:
        # Seed catalogs
        seed_medical_conditions()
        seed_food_intolerances()
        seed_dietary_preferences()
        seed_ingredients()
        seed_recipe_tags()
        seed_sample_recipes()
        
        db.session.commit()
        print("✅ Todos los datos fueron sembrados exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error sembrando datos: {str(e)}")
        db.session.rollback()
        return False

def seed_medical_conditions():
    """Sembrar condiciones médicas."""
    conditions = [
        {'condition_name': 'Diabetes Tipo 1', 'description': 'Diabetes mellitus tipo 1', 'severity_level': 'high'},
        {'condition_name': 'Diabetes Tipo 2', 'description': 'Diabetes mellitus tipo 2', 'severity_level': 'high'},
        {'condition_name': 'Hipertensión', 'description': 'Presión arterial alta', 'severity_level': 'medium'},
        {'condition_name': 'Enfermedad Cardiovascular', 'description': 'Problemas del corazón', 'severity_level': 'high'},
        {'condition_name': 'Enfermedad Gastrointestinal', 'description': 'Problemas digestivos', 'severity_level': 'medium'},
        {'condition_name': 'Enfermedad Renal', 'description': 'Problemas de riñón', 'severity_level': 'high'},
        {'condition_name': 'Enfermedad Celíaca', 'description': 'Intolerancia al gluten', 'severity_level': 'high'},
        {'condition_name': 'Obesidad', 'description': 'Exceso de peso corporal', 'severity_level': 'medium'},
    ]
    
    for condition_data in conditions:
        existing = db.session.query(MedicalCondition).filter(
            MedicalCondition.condition_name == condition_data['condition_name']
        ).first()
        if not existing:
            condition = MedicalCondition(**condition_data)
            db.session.add(condition)

def seed_food_intolerances():
    """Sembrar intolerancias alimentarias."""
    intolerances = [
        {'intolerance_name': 'Lactosa', 'description': 'Intolerancia a productos lácteos'},
        {'intolerance_name': 'Gluten', 'description': 'Intolerancia al gluten'},
        {'intolerance_name': 'Nueces', 'description': 'Alergia a frutos secos'},
        {'intolerance_name': 'Mariscos', 'description': 'Alergia a mariscos y crustáceos'},
        {'intolerance_name': 'Huevo', 'description': 'Alergia al huevo'},
        {'intolerance_name': 'Soya', 'description': 'Alergia a la soya'},
    ]
    
    for intolerance_data in intolerances:
        existing = db.session.query(FoodIntolerance).filter(
            FoodIntolerance.intolerance_name == intolerance_data['intolerance_name']
        ).first()
        if not existing:
            intolerance = FoodIntolerance(**intolerance_data)
            db.session.add(intolerance)

def seed_dietary_preferences():
    """Sembrar preferencias dietéticas."""
    preferences = [
        {'preference_name': 'Vegetariano', 'description': 'No consume carne ni pescado'},
        {'preference_name': 'Vegano', 'description': 'No consume productos de origen animal'},
        {'preference_name': 'Pescetariano', 'description': 'Consume pescado pero no carne'},
        {'preference_name': 'Bajo en Carbohidratos', 'description': 'Dieta baja en carbohidratos'},
        {'preference_name': 'Mediterránea', 'description': 'Dieta mediterránea'},
        {'preference_name': 'Ketogénica', 'description': 'Dieta alta en grasas, baja en carbohidratos'},
    ]
    
    for preference_data in preferences:
        existing = db.session.query(DietaryPreference).filter(
            DietaryPreference.preference_name == preference_data['preference_name']
        ).first()
        if not existing:
            preference = DietaryPreference(**preference_data)
            db.session.add(preference)

def seed_ingredients():
    """Sembrar ingredientes básicos."""
    ingredients = [
        {'ingredient_name': 'avena integral', 'category': 'cereales', 'calories_per_100g': 389, 'protein_per_100g': 16.9, 'carbs_per_100g': 66.3, 'fat_per_100g': 6.9, 'fiber_per_100g': 10.6},
        {'ingredient_name': 'leche de almendras', 'category': 'lácteos', 'calories_per_100g': 17, 'protein_per_100g': 0.6, 'carbs_per_100g': 1.5, 'fat_per_100g': 1.1, 'fiber_per_100g': 0.2},
        {'ingredient_name': 'frutos rojos mixtos', 'category': 'frutas', 'calories_per_100g': 57, 'protein_per_100g': 0.7, 'carbs_per_100g': 14.5, 'fat_per_100g': 0.3, 'fiber_per_100g': 2.4},
        {'ingredient_name': 'canela', 'category': 'especias', 'calories_per_100g': 247, 'protein_per_100g': 4.0, 'carbs_per_100g': 80.6, 'fat_per_100g': 1.2, 'fiber_per_100g': 53.1},
        {'ingredient_name': 'pechuga de pollo', 'category': 'proteínas', 'calories_per_100g': 165, 'protein_per_100g': 31.0, 'carbs_per_100g': 0.0, 'fat_per_100g': 3.6, 'fiber_per_100g': 0.0},
        {'ingredient_name': 'quinoa', 'category': 'cereales', 'calories_per_100g': 368, 'protein_per_100g': 14.1, 'carbs_per_100g': 64.2, 'fat_per_100g': 6.1, 'fiber_per_100g': 7.0},
        {'ingredient_name': 'brócoli', 'category': 'vegetales', 'calories_per_100g': 34, 'protein_per_100g': 2.8, 'carbs_per_100g': 6.6, 'fat_per_100g': 0.4, 'fiber_per_100g': 2.6},
        {'ingredient_name': 'salmón', 'category': 'proteínas', 'calories_per_100g': 208, 'protein_per_100g': 25.4, 'carbs_per_100g': 0.0, 'fat_per_100g': 12.4, 'fiber_per_100g': 0.0},
        {'ingredient_name': 'espinaca', 'category': 'vegetales', 'calories_per_100g': 23, 'protein_per_100g': 2.9, 'carbs_per_100g': 3.6, 'fat_per_100g': 0.4, 'fiber_per_100g': 2.2},
        {'ingredient_name': 'aceite de oliva', 'category': 'aceites', 'calories_per_100g': 884, 'protein_per_100g': 0.0, 'carbs_per_100g': 0.0, 'fat_per_100g': 100.0, 'fiber_per_100g': 0.0},
    ]
    
    for ingredient_data in ingredients:
        existing = db.session.query(Ingredient).filter(
            Ingredient.ingredient_name == ingredient_data['ingredient_name']
        ).first()
        if not existing:
            ingredient = Ingredient(**ingredient_data)
            db.session.add(ingredient)

def seed_recipe_tags():
    """Sembrar tags de recetas."""
    tags = [
        {'tag_name': 'Apto para Diabéticos', 'color': '#10b981'},
        {'tag_name': 'Bajo en Calorías', 'color': '#3b82f6'},
        {'tag_name': 'Alto en Proteína', 'color': '#8b5cf6'},
        {'tag_name': 'Rico en Fibra', 'color': '#f59e0b'},
        {'tag_name': 'Sin Lactosa', 'color': '#ef4444'},
        {'tag_name': 'Sin Gluten', 'color': '#06b6d4'},
        {'tag_name': 'Vegano', 'color': '#22c55e'},
        {'tag_name': 'Energético', 'color': '#f97316'},
        {'tag_name': 'Nutritivo', 'color': '#059669'},
        {'tag_name': 'Ligero', 'color': '#7c3aed'}
    ]
    
    for tag_data in tags:
        existing = db.session.query(RecipeTag).filter(
            RecipeTag.tag_name == tag_data['tag_name']
        ).first()
        if not existing:
            tag = RecipeTag(**tag_data)
            db.session.add(tag)

def seed_sample_recipes():
    """Sembrar recetas de ejemplo."""
    db.session.flush()  # Para obtener los IDs de ingredientes
    
    # Obtener ingredientes
    avena = db.session.query(Ingredient).filter(Ingredient.ingredient_name == 'avena integral').first()
    leche_almendras = db.session.query(Ingredient).filter(Ingredient.ingredient_name == 'leche de almendras').first()
    frutos_rojos = db.session.query(Ingredient).filter(Ingredient.ingredient_name == 'frutos rojos mixtos').first()
    pollo = db.session.query(Ingredient).filter(Ingredient.ingredient_name == 'pechuga de pollo').first()
    quinoa = db.session.query(Ingredient).filter(Ingredient.ingredient_name == 'quinoa').first()
    salmon = db.session.query(Ingredient).filter(Ingredient.ingredient_name == 'salmón').first()
    espinaca = db.session.query(Ingredient).filter(Ingredient.ingredient_name == 'espinaca').first()
    
    # Crear recetas de ejemplo para cada tipo de comida
    recipes_data = [
        # Desayunos
        {
            'recipe_name': 'Avena Integral con Frutos Rojos 1',
            'meal_type': 'breakfast',
            'total_calories': 320,
            'total_protein': 12,
            'total_carbs': 45,
            'total_fiber': 10,
            'instructions': 'Cocinar avena con leche de almendras. Agregar frutos rojos.',
            'ingredients': [(avena, 0.5, 'taza'), (leche_almendras, 1, 'taza'), (frutos_rojos, 0.5, 'taza')]
        },
        # Crear 10 recetas de cada tipo
    ]
    
    # Generar múltiples recetas de cada tipo
    meal_types = ['breakfast', 'lunch', 'dinner'] 
    for meal_type in meal_types:
        for i in range(1, 11):  # 10 recetas de cada tipo
            if meal_type == 'breakfast':
                base_name = f'Desayuno Saludable {i}'
                calories = 280 + (i * 10)
                protein = 10 + i
                carbs = 35 + i
                fiber = 5 + i
                ingredients = [(avena, 0.5, 'taza'), (leche_almendras, 1, 'taza')]
            elif meal_type == 'lunch':
                base_name = f'Almuerzo Balanceado {i}'
                calories = 420 + (i * 15)
                protein = 30 + i
                carbs = 35 + i
                fiber = 6 + i
                ingredients = [(pollo, 100, 'gramos'), (quinoa, 0.5, 'taza')]
            else:  # dinner
                base_name = f'Cena Ligera {i}'
                calories = 300 + (i * 8)
                protein = 25 + i
                carbs = 15 + i
                fiber = 5 + i
                ingredients = [(salmon, 100, 'gramos'), (espinaca, 1, 'taza')]
            
            # Verificar si la receta ya existe
            existing_recipe = db.session.query(Recipe).filter(
                Recipe.recipe_name == base_name
            ).first()
            
            if not existing_recipe:
                recipe = Recipe(
                    recipe_name=base_name,
                    description=f'Receta {meal_type} número {i}',
                    meal_type=meal_type,
                    preparation_time=10,
                    cooking_time=15,
                    servings=1,
                    difficulty_level='easy',
                    total_calories=Decimal(str(calories)),
                    total_protein=Decimal(str(protein)),
                    total_carbs=Decimal(str(carbs)),
                    total_fat=Decimal('10'),
                    total_fiber=Decimal(str(fiber)),
                    instructions=f'1. Preparar ingredientes básicos.\n2. Cocinar según necesidad.\n3. Servir fresco.',
                    is_active=True
                )
                
                db.session.add(recipe)
                db.session.flush()  # Para obtener el ID de la receta
                
                # Agregar ingredientes
                for ingredient, quantity, unit in ingredients:
                    if ingredient:
                        recipe_ingredient = RecipeIngredient(
                            recipe_id=recipe.id,
                            ingredient_id=ingredient.id,
                            quantity=Decimal(str(quantity)),
                            unit=unit
                        )
                        db.session.add(recipe_ingredient)
    
    print(f"✅ Recetas de ejemplo creadas")

if __name__ == '__main__':
    # This allows running the seed script directly
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    from app import create_app
    app = create_app('development')
    
    with app.app_context():
        seed_all_data()
