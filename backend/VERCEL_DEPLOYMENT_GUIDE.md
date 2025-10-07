# Vercel Deployment Guide for PactoC Backend

## Prerequisites

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

## Environment Variables Setup

Before deploying, you need to set these environment variables in Vercel:

### Required Variables:
```bash
# Database (PostgreSQL required for production)
DATABASE_URL=postgresql://username:password@host:port/database

# Firebase (for authentication)
FIREBASE_SERVICE_ACCOUNT_KEY={"type": "service_account", "project_id": "your_project_id", ...}

# Flask
SECRET_KEY=your_production_secret_key
FLASK_ENV=production

# CORS
CORS_ORIGINS=https://your-frontend-domain.vercel.app,https://your-custom-domain.com
```

### Set Environment Variables in Vercel:
```bash
# Set DATABASE_URL
vercel env add DATABASE_URL

# Set Firebase service account key (paste the full JSON)
vercel env add FIREBASE_SERVICE_ACCOUNT_KEY

# Set secret key  
vercel env add SECRET_KEY

# Set CORS origins
vercel env add CORS_ORIGINS
```

## Database Setup

You'll need a PostgreSQL database. Options:

1. **Vercel Postgres** (Recommended):
   - Go to your Vercel dashboard
   - Create a new Postgres database
   - Copy the connection string to `DATABASE_URL`

2. **External PostgreSQL** (Railway, Supabase, etc.):
   - Create a PostgreSQL database
   - Get the connection string
   - Set it as `DATABASE_URL`

## Deployment Steps

1. **Test configuration locally**:
   ```bash
   cd backend
   python test_vercel_deployment.py
   ```

2. **Deploy to Vercel**:
   ```bash
   cd backend
   vercel --prod
   ```

3. **Verify deployment**:
   - Visit your Vercel URL
   - Check `/health` endpoint
   - Check `/api/health` endpoint

## Troubleshooting

### Common Issues:

1. **Database Connection Errors**:
   - Verify `DATABASE_URL` is correctly set
   - Ensure your database allows connections from Vercel

2. **Import Errors**:
   - Check that all dependencies are in `requirements.txt`
   - Verify Python version compatibility

3. **Firebase Errors**:
   - Ensure `FIREBASE_SERVICE_ACCOUNT_KEY` is properly formatted JSON
   - Check Firebase project permissions

### Debugging:
- Check Vercel function logs in dashboard
- Use the fallback routes for basic health checks
- Test individual endpoints after deployment

## File Structure for Vercel

```
backend/
├── api/
│   └── index.py          # Main entry point for Vercel
├── app/                  # Your Flask application
├── vercel.json          # Vercel configuration
├── requirements.txt     # Python dependencies
└── .vercelignore       # Files to exclude from deployment
```

## Production Checklist

- [ ] Environment variables set in Vercel
- [ ] Database accessible from internet
- [ ] CORS origins configured correctly
- [ ] Firebase service account key valid
- [ ] Test deployment works locally
- [ ] All routes accessible after deployment
