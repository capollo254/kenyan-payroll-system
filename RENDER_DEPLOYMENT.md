# Render Deployment Guide

## Files Created for Deployment

1. **render.yaml** - Render service configuration
2. **build.sh** - Build script for deployment
3. **requirements.txt** - Updated with production dependencies
4. **settings.py** - Updated for production/development environments
5. **.env.example** - Environment variables template

## Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 2. Deploy on Render
1. Go to [render.com](https://render.com)
2. Sign up/login and connect your GitHub account
3. Click "New +" → "Web Service"
4. Select your repository
5. Render will automatically detect the `render.yaml` file

### 3. Configuration
Render will automatically configure:
- **Build Command**: `./build.sh`
- **Start Command**: `cd backend && gunicorn kenyan_payroll_project.wsgi:application`
- **Environment**: Python 3.11.4
- **Database**: PostgreSQL (created automatically)

### 4. Environment Variables (Auto-configured)
- `DATABASE_URL` - Set by PostgreSQL service
- `SECRET_KEY` - Auto-generated
- `DEBUG` - Set to False
- `DJANGO_SUPERUSER_*` - Admin account creation

### 5. Post-Deployment
1. Your app will be available at: `https://kenyan-payroll-system.onrender.com`
2. Admin panel: `https://kenyan-payroll-system.onrender.com/admin/`
3. API endpoints: `https://kenyan-payroll-system.onrender.com/api/`

### 6. Update CORS Settings
After deployment, update the CORS_ALLOWED_ORIGINS in settings.py with your actual Render URL.

## Features Deployed
- ✅ Complete KRA-compliant payroll system
- ✅ Employee management
- ✅ Payroll processing
- ✅ Public calculator API
- ✅ Admin interface
- ✅ PostgreSQL database
- ✅ Static file serving
- ✅ Automatic admin user creation

## Troubleshooting
- Check build logs in Render dashboard
- Verify environment variables are set
- Ensure database migrations completed
- Check static files are collected

## Local Development
To run locally after these changes:
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```