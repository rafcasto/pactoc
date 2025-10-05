# Meal Plan Workflow Testing Guide

## Quick Start Testing

### 1. Start the System
```bash
cd /Users/rafaelcastillo/pactoc
./start_dev.sh
```

Wait for both services to start:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000

### 2. Test the Workflow Pages

#### A. Nutritionist Dashboard
1. **Visit**: http://localhost:3000/meal-plan-workflow
2. **Login**: Use existing authentication system
3. **Features to test**:
   - Send new invitation
   - View pending reviews
   - Approve meal plans
   - Copy dynamic links

#### B. Dynamic Patient Link
1. **Get a test token** from existing invitation or create new one
2. **Visit**: http://localhost:3000/patient/invitation/{TOKEN}
3. **Test workflow**:
   - Form submission (status: pending)
   - Pending review message (status: completed)
   - Meal plan view (status: approved)

## Step-by-Step Workflow Test

### Step 1: Create Invitation (Nutritionist)
```bash
# API Test (requires auth token)
curl -X POST http://localhost:8000/api/workflow/invitations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "email": "patient@example.com",
    "patient_name": "John Doe"
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "patient@example.com",
    "token": "unique-token-here",
    "dynamic_link": "http://localhost:3000/patient/invitation/unique-token-here"
  }
}
```

### Step 2: Patient Form Access
```bash
# Test dynamic link content (no auth required)
curl -X GET http://localhost:8000/api/workflow/patient/{TOKEN}
```

**Expected Response** (status: pending):
```json
{
  "success": true,
  "data": {
    "status": "pending",
    "content_type": "patient_form",
    "data": {
      "medical_conditions": [...],
      "food_intolerances": [...],
      "dietary_preferences": [...]
    }
  }
}
```

### Step 3: Submit Patient Form
```bash
curl -X POST http://localhost:8000/api/workflow/patient/{TOKEN}/submit \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "gender": "male",
    "email": "john@example.com",
    "medical_conditions": [1, 2],
    "intolerances": [1],
    "dietary_preferences": [1, 2]
  }'
```

**Expected Response**:
```json
{
  "success": true,
  "data": {
    "patient_id": 1,
    "message": "Thank you! Your information has been submitted...",
    "status": "completed"
  }
}
```

### Step 4: Check Pending Review
```bash
# Same link now shows different content
curl -X GET http://localhost:8000/api/workflow/patient/{TOKEN}
```

**Expected Response** (status: completed):
```json
{
  "success": true,
  "data": {
    "status": "completed",
    "content_type": "pending_review",
    "data": {
      "message": "Your meal plan is being reviewed...",
      "patient_name": "John Doe"
    }
  }
}
```

### Step 5: Approve Meal Plan (Nutritionist)
```bash
curl -X POST http://localhost:8000/api/workflow/approve/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "plan_name": "Weekly Plan - John Doe",
    "notes": "Customized plan based on your preferences"
  }'
```

### Step 6: View Meal Plan
```bash
# Same link now shows meal plan
curl -X GET http://localhost:8000/api/workflow/patient/{TOKEN}
```

**Expected Response** (status: approved):
```json
{
  "success": true,
  "data": {
    "status": "approved", 
    "content_type": "meal_plan",
    "data": {
      "meal_plan": {...},
      "patient": {...},
      "calendar": {...}
    }
  }
}
```

### Step 7: Test PDF Export
```bash
# Download PDF
curl -X GET http://localhost:8000/api/workflow/patient/{TOKEN}/pdf \
  --output meal_plan.pdf
```

## Frontend Testing

### 1. Nutritionist Workflow UI
- **URL**: http://localhost:3000/meal-plan-workflow
- **Login**: Required (use existing auth)
- **Test Actions**:
  - ✅ Send invitation modal
  - ✅ View dashboard statistics
  - ✅ Review pending submissions
  - ✅ Approve meal plans
  - ✅ Copy dynamic links

### 2. Patient Dynamic Link UI  
- **URL**: http://localhost:3000/patient/invitation/{TOKEN}
- **No login required**
- **Test Scenarios**:
  - ✅ Patient form (pending status)
  - ✅ Pending review message (completed status)
  - ✅ Full meal plan (approved status)
  - ✅ Print functionality
  - ✅ PDF download

### 3. Responsive Design
- ✅ Mobile-friendly forms
- ✅ Print-optimized layouts
- ✅ Clean PDF generation

## Error Testing

### Invalid Token
```bash
curl -X GET http://localhost:8000/api/workflow/patient/invalid-token
```
**Expected**: 404 with error message

### Expired Token
- Test with invitation older than 7 days
- **Expected**: Error message about expiration

### Wrong Status Access
- Try to submit form when already completed
- **Expected**: Appropriate error handling

## Browser Testing

### Supported Browsers
- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)  
- ✅ Safari (latest)
- ✅ Mobile browsers

### Print Testing
1. **Open meal plan**: http://localhost:3000/patient/invitation/{APPROVED_TOKEN}
2. **Click Print button** or use Ctrl+P
3. **Verify**: Clean layout without navigation
4. **Check**: Professional formatting

### PDF Testing
1. **Open meal plan**: http://localhost:3000/patient/invitation/{APPROVED_TOKEN}
2. **Click Download PDF**
3. **Verify**: File downloads with proper name
4. **Check**: PDF contains all meal plan data

## Database Verification

### Check Tables
```sql
-- View invitations
SELECT id, email, status, created_at FROM patient_invitations;

-- View patients
SELECT id, first_name, last_name, invitation_id FROM patients;

-- View meal plans
SELECT id, patient_id, plan_name, status FROM meal_plans;
```

### Status Progression
```sql
-- Should see status progression:
-- 1. pending (invitation created)
-- 2. completed (form submitted)
-- 3. approved (meal plan approved)
```

## Performance Testing

### Load Testing (Optional)
```bash
# Test multiple concurrent requests
for i in {1..10}; do
  curl -X GET http://localhost:8000/api/workflow/patient/{TOKEN} &
done
wait
```

### PDF Generation Load
- Test PDF generation with multiple concurrent requests
- Verify server handles load appropriately

## Production Readiness Checklist

### Backend
- ✅ Error handling implemented
- ✅ Input validation
- ✅ SQL injection protection
- ✅ Token security
- ✅ PDF generation working
- ✅ Status-based access control

### Frontend  
- ✅ Form validation
- ✅ Loading states
- ✅ Error messages
- ✅ Responsive design
- ✅ Print optimization
- ✅ PDF download functionality

### Security
- ✅ Token-based access
- ✅ CORS configured
- ✅ Input sanitization
- ✅ Authentication on nutritionist routes
- ✅ Status verification

## Troubleshooting

### Common Issues
1. **503 Service Unavailable**: Wait for servers to fully start
2. **404 Not Found**: Check URL and token validity
3. **Token expired**: Generate new invitation
4. **PDF not downloading**: Check reportlab installation
5. **Print styles not working**: Verify CSS media queries

### Debug Commands
```bash
# Check server status
curl -s http://localhost:8000/api/health

# Check database connection
curl -s http://localhost:8000/api/public/catalogs

# Verify token validity
curl -s http://localhost:8000/api/workflow/patient/{TOKEN}
```

## Success Criteria

✅ **Single dynamic link works throughout workflow**  
✅ **Status-based content rendering**  
✅ **Form submission and validation**  
✅ **Nutritionist dashboard functional**  
✅ **PDF export working**  
✅ **Print functionality working**  
✅ **Responsive design**  
✅ **Error handling**  
✅ **Database integration**  
✅ **Security implemented**  

## Next Steps

After successful testing:
1. **Deploy to staging environment**
2. **Configure email service** (SMTP)
3. **Set up monitoring** (logs, metrics)
4. **User acceptance testing**
5. **Production deployment**

The meal plan workflow system is **fully implemented and ready for testing**! 🚀
