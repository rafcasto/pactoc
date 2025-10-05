# Sistema de Recetas Dietéticas - Documentación Completa

## 🎯 DESCRIPCIÓN DEL SISTEMA

Este es un sistema completo de recetas dietéticas que permite a los nutricionistas crear invitaciones para que los pacientes completen su perfil médico de forma pública (sin login) y reciban automáticamente un plan de comidas personalizado.

## 🏗️ ARQUITECTURA DEL SISTEMA

### Backend (Flask + SQLAlchemy + SQLite)
- **Base de datos**: SQLite (configurable a PostgreSQL)
- **ORM**: SQLAlchemy con migraciones
- **Autenticación**: Firebase Auth (solo para panel admin)
- **API pública**: Sin autenticación para pacientes

### Frontend (Next.js 15 + React 19 + TypeScript)
- **Framework**: Next.js con App Router
- **UI**: Tailwind CSS + Lucide Icons
- **Formularios**: React Hook Form + Zod
- **Estado**: React state (no Redux necesario)

## 📋 CARACTERÍSTICAS IMPLEMENTADAS

### ✅ Formulario Público de Pacientes
- Acceso vía link único `/complete-profile/{token}`
- Validación de token automática
- Formulario responsive con diseño minimalista
- Recolección de:
  - Información personal (nombre, edad, género, contacto)
  - Condiciones médicas múltiples
  - Intolerancias alimentarias
  - Preferencias dietéticas
- Validaciones completas del lado cliente y servidor

### ✅ Generación Automática de Planes
- Algoritmo inteligente de distribución de recetas
- Filtrado por restricciones médicas e intolerancias
- Creación automática de plan semanal (lunes a domingo)
- Asignación de horarios (desayuno 8:00, almuerzo 13:00, cena 19:00)
- Variedad garantizada (no repetir recetas en la semana)

### ✅ Vista Pública del Plan de Comidas
- Acceso vía link único `/my-meal-plan/{token}`
- Diseño igual al artifact "Patient Diet Recipe System"
- Cards detalladas por cada comida con:
  - Información nutricional (calorías, proteínas, carbohidratos, fibra)
  - Tags de compatibilidad (Apto para Diabéticos, Sin Lactosa, etc.)
  - Lista de ingredientes con cantidades
  - Instrucciones numeradas paso a paso
  - Tiempos de preparación y cocción
- Organización por días de la semana
- Información personalizada del paciente

### ✅ Base de Datos Completa
- 13 tablas relacionales implementadas
- Catálogos pre-poblados:
  - 8+ condiciones médicas
  - 6+ intolerancias alimentarias
  - 6+ preferencias dietéticas
  - 10+ ingredientes base con valores nutricionales
  - 10+ tags de recetas
- 30 recetas de ejemplo (10 desayunos, 10 almuerzos, 10 cenas)
- Sistema de tokens para acceso público (invitaciones y planes)

## 🚀 INSTALACIÓN Y CONFIGURACIÓN

### Requisitos Previos
- Python 3.11+
- Node.js 18+
- npm o yarn

### Instalación Backend

1. **Clonar el repositorio**
```bash
cd /Users/rafaelcastillo/pactoc/backend
```

2. **Instalar dependencias Python**
```bash
pip3 install flask flask-cors flask-sqlalchemy flask-migrate psycopg2-binary python-dotenv
```

3. **Inicializar la base de datos y datos de ejemplo**
```bash
python3.11 init_system.py
```

4. **Crear invitación de prueba**
```bash
python3.11 create_test_invitation.py
```

5. **Ejecutar servidor backend**
```bash
python3.11 run_diet_server.py
```

### Instalación Frontend

1. **Ir al directorio frontend**
```bash
cd /Users/rafaelcastillo/pactoc/frontend
```

2. **Instalar dependencias**
```bash
npm install
```

3. **Ejecutar servidor frontend**
```bash
npm run dev
```

## 🔗 ENDPOINTS API IMPLEMENTADOS

### Rutas Públicas (Sin Autenticación)

#### `GET /api/public/invitations/{token}`
Validar token de invitación
```json
{
  "valid": true,
  "invitation": {
    "invitation_id": 123,
    "email": "paciente@test.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "expires_at": "2025-10-08T19:12:58Z"
  }
}
```

#### `POST /api/public/profiles/{token}`
Completar perfil del paciente y generar plan automáticamente
```json
{
  "first_name": "Juan",
  "last_name": "Pérez",
  "date_of_birth": "1985-03-15",
  "gender": "male",
  "email": "juan@test.com",
  "phone": "+503 7777-7777",
  "medical_conditions": [1, 2],
  "intolerances": [3],
  "dietary_preferences": [2, 5]
}
```

Respuesta:
```json
{
  "success": true,
  "patient_id": 456,
  "meal_plan_token": "xyz789abc...",
  "meal_plan_link": "/my-meal-plan/xyz789abc",
  "message": "Perfil completado. Tu plan personalizado está listo."
}
```

#### `GET /api/public/meal-plans/{token}`
Ver plan de comidas del paciente
```json
{
  "patient": {
    "first_name": "Juan",
    "conditions": ["Diabetes Tipo 2"],
    "intolerances": ["Lactosa"]
  },
  "meal_plan": {
    "plan_id": 789,
    "start_date": "2025-10-07",
    "end_date": "2025-10-13",
    "meals": [
      {
        "day": "Lunes",
        "meals": [
          {
            "type": "Desayuno",
            "time": "08:00",
            "recipe": {
              "recipe_name": "Avena Integral con Frutos Rojos",
              "calories": 320,
              "protein": 12,
              "carbs": 45,
              "fiber": 8,
              "tags": ["Apto para Diabéticos", "Sin Lactosa"],
              "ingredients": ["½ taza de avena integral", "1 taza de leche de almendras"],
              "instructions": ["1. Cocinar la avena...", "2. Agregar frutos rojos..."]
            }
          }
        ]
      }
    ]
  }
}
```

#### `GET /api/public/catalogs`
Obtener catálogos para el formulario
```json
{
  "medical_conditions": [...],
  "food_intolerances": [...],
  "dietary_preferences": [...]
}
```

## 🎨 COMPONENTES FRONTEND IMPLEMENTADOS

### Páginas
- `app/complete-profile/[token]/page.tsx` - Formulario público del paciente
- `app/my-meal-plan/[token]/page.tsx` - Vista del plan de comidas
- `app/profile-completed/page.tsx` - Página de confirmación

### Características de Diseño
- **Mobile-first**: Responsive en todos los dispositivos
- **Gradientes suaves**: Fondo slate-50 a slate-100
- **Cards minimalistas**: Bordes redondeados, sombras sutiles
- **Código de colores**:
  - 🔵 Azul: Información personal
  - 🔴 Rojo: Condiciones médicas
  - 🟠 Naranja: Intolerancias
  - 🟢 Verde: Preferencias dietéticas
- **Iconografía**: Lucide React icons
- **Loading states**: En todas las operaciones async
- **Manejo de errores**: Mensajes claros y útiles

## 🔄 FLUJO COMPLETO DE USUARIO

1. **Admin crea invitación** desde panel administrativo
2. **Sistema genera token único** con expiración de 7 días
3. **Paciente recibe link**: `app.com/complete-profile/abc123`
4. **Paciente abre link** → Sistema valida token automáticamente
5. **Paciente completa formulario** con información médica
6. **Sistema procesa datos**:
   - Crea registro de paciente
   - Filtra recetas compatibles con restricciones
   - Genera plan semanal automáticamente
   - Crea token de visualización del plan
7. **Paciente es redirigido**: `app.com/my-meal-plan/xyz789`
8. **Paciente ve su plan personalizado** con recetas detalladas
9. **Admin puede revisar** el paciente en su panel y modificar plan si necesario

## 🧮 ALGORITMO DE GENERACIÓN DE PLANES

### Proceso de Generación
1. **Análisis del paciente**: Obtiene condiciones médicas, intolerancias y preferencias
2. **Mapeo de restricciones**: Convierte intolerancias en ingredientes prohibidos
3. **Filtrado de recetas**: Excluye recetas que contengan ingredientes restringidos
4. **Validación de disponibilidad**: Verifica que haya al menos 7 recetas por tipo de comida
5. **Distribución inteligente**: Asigna recetas aleatoriamente para evitar repeticiones
6. **Creación del plan**: Genera plan semanal con horarios establecidos
7. **Generación de token**: Crea acceso público permanente al plan

### Restricciones Implementadas
- **Lactosa**: Excluye leche, queso, yogur, mantequilla, crema
- **Gluten**: Excluye harina de trigo, avena, cebada, centeno
- **Nueces**: Excluye nueces, almendras, pistachos, avellanas
- **Mariscos**: Excluye camarones, langosta, cangrejo, mejillones
- **Huevo**: Excluye huevo y derivados
- **Soya**: Excluye salsa de soya, tofu, tempeh, leche de soya

## 🛡️ SEGURIDAD IMPLEMENTADA

### Tokens de Seguridad
- **Generación**: `secrets.token_urlsafe(32)` (256 bits de entropía)
- **Unicidad**: Índice único en base de datos
- **Expiración**: Invitaciones expiran en 7 días, planes no expiran
- **Validación**: Verificación automática en cada request

### Validaciones
- **Formulario**: Validación cliente y servidor
- **Datos**: Sanitización de inputs
- **Edad**: Rango válido 1-120 años
- **Email**: Formato RFC válido
- **Restricciones**: Al menos 1 condición médica o intolerancia

### Sin Exposición de IDs
- URLs públicas solo usan tokens únicos
- No se exponen IDs internos de base de datos
- Acceso controlado por tokens temporales

## 📊 ESTRUCTURA DE BASE DE DATOS

### Tablas Principales
```sql
-- Invitaciones
patient_invitations (id, token, email, status, expires_at, ...)

-- Pacientes  
patients (id, invitation_id, first_name, last_name, date_of_birth, ...)

-- Catálogos
medical_conditions (id, condition_name, severity_level, ...)
food_intolerances (id, intolerance_name, description, ...)
dietary_preferences (id, preference_name, description, ...)

-- Relaciones Many-to-Many
patient_medical_conditions (patient_id, condition_id, ...)
patient_intolerances (patient_id, intolerance_id, severity, ...)
patient_dietary_preferences (patient_id, preference_id, ...)

-- Sistema de Recetas
ingredients (id, ingredient_name, calories_per_100g, protein_per_100g, ...)
recipes (id, recipe_name, meal_type, total_calories, instructions, ...)
recipe_ingredients (recipe_id, ingredient_id, quantity, unit, ...)
recipe_tags (id, tag_name, color, ...)
recipe_tag_assignments (recipe_id, tag_id, ...)

-- Planes de Comidas
meal_plans (id, patient_id, start_date, end_date, status, ...)
meal_plan_meals (id, plan_id, recipe_id, day_of_week, meal_type, scheduled_time, ...)
meal_plan_tokens (id, plan_id, token, expires_at, ...)
```

## 🧪 TESTING Y DEBUG

### Scripts de Utilidad
- `init_system.py` - Inicializar sistema completo
- `create_test_invitation.py` - Crear invitación de prueba
- `run_diet_server.py` - Servidor de desarrollo
- `seed_data.py` - Poblar datos de ejemplo

### URLs de Prueba
Con la invitación de ejemplo:
- **Formulario**: `http://localhost:3000/complete-profile/QizKtpixpDYa6_UwgWgW54Rh0GcTUO2x8oblSAloT-E`
- **API Backend**: `http://localhost:8000/api/public/`
- **Validar token**: `http://localhost:8000/api/public/invitations/{token}`

## 🔧 CONFIGURACIÓN DE ENTORNO

### Variables de Entorno Backend
```bash
FLASK_ENV=development
DATABASE_URL=sqlite:///pactoc_dev.db  # o postgresql://...
SECRET_KEY=your-secret-key
```

### Variables de Entorno Frontend
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📈 PRÓXIMAS MEJORAS

### Funcionalidades Adicionales
- [ ] Generación de PDF para planes de comidas
- [ ] Sistema de notificaciones por email
- [ ] Dashboard de seguimiento para pacientes
- [ ] Integración con calendarios
- [ ] Sistema de feedback de recetas
- [ ] Cálculo automático de valores nutricionales
- [ ] Sugerencias de sustitución de ingredientes
- [ ] Planes de compras automáticos

### Mejoras Técnicas
- [ ] Cache de consultas frecuentes
- [ ] Optimización de queries de base de datos
- [ ] Tests automatizados (Jest + Pytest)
- [ ] CI/CD pipeline
- [ ] Monitoreo y logging avanzado
- [ ] Backup automático de base de datos
- [ ] Rate limiting más granular

## 🚀 DESPLIEGUE EN PRODUCCIÓN

### Backend
1. Configurar PostgreSQL en producción
2. Actualizar `DATABASE_URL` con URL de PostgreSQL
3. Configurar variables de entorno de producción
4. Usar servidor WSGI (Gunicorn)

### Frontend
1. Configurar `NEXT_PUBLIC_API_URL` con URL de producción
2. Ejecutar `npm run build`
3. Desplegar en Vercel, Netlify o servidor propio

## 📞 SOPORTE

Para preguntas o problemas con el sistema:
1. Revisar logs del servidor backend
2. Verificar conexión a base de datos
3. Confirmar que tokens no hayan expirado
4. Verificar que catálogos estén poblados

---

**Desarrollado con ❤️ usando Flask, Next.js y SQLAlchemy**

*Sistema completo de recetas dietéticas - Versión 1.0*
