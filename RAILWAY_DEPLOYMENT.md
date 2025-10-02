# Railway Deployment Guide - Kenya Payroll System

## Why Railway?
- Simpler than Render for Django apps
- Better Python version management
- Automatic PostgreSQL database
- Zero-config deployments
- Free tier available

## Files Created
1. **Procfile** - Defines how Railway runs your app
2. **railway.toml** - Railway configuration
3. **.env.railway** - Environment variables template
4. **Updated settings.py** - Railway-specific configuration

## Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

### 2. Deploy on Railway

1. **Sign up at [railway.app](https://railway.app)**
2. **Connect GitHub account**
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your repository**: `capollo254/LekoHR`
6. **Railway will auto-detect your Python app**

### 3. Add PostgreSQL Database

1. **In your Railway project dashboard**
2. **Click "New Service" → "Database" → "PostgreSQL"**
3. **Railway automatically creates DATABASE_URL**

### 4. Configure Environment Variables

In Railway dashboard, add these variables:
```
DEBUG=False
SECRET_KEY=your-generated-secret-key
RAILWAY_ENVIRONMENT=production
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@payroll.com
DJANGO_SUPERUSER_PASSWORD=your-secure-password
```

### 5. Deploy and Monitor

1. **Railway automatically deploys after GitHub push**
2. **Monitor deployment in Railway dashboard**
3. **Check build logs for any issues**

## Your App URLs

After deployment, your app will be available at:
- **Main App**: `https://your-app-name.up.railway.app`
- **Admin Panel**: `https://your-app-name.up.railway.app/admin/`
- **API**: `https://your-app-name.up.railway.app/api/`
- **Calculator**: `https://your-app-name.up.railway.app/calculator/`

## Features Deployed

✅ **Complete KRA-compliant payroll system**
✅ **Employee management with profile pictures**
✅ **Payroll processing with all reliefs**
✅ **Public payroll calculator**
✅ **Admin interface**
✅ **REST API endpoints**
✅ **PostgreSQL database**
✅ **Static file serving**
✅ **Automatic migrations**

## Advantages over Render

- **Faster deployments**
- **Better error messages**
- **Simpler configuration**
- **More reliable Python version handling**
- **Automatic environment detection**

## Troubleshooting

### Common Issues:
1. **Build fails**: Check build logs in Railway dashboard
2. **Database errors**: Ensure PostgreSQL service is added
3. **Static files not loading**: Verify collectstatic runs in build
4. **Admin access**: Check superuser environment variables

### Logs:
View logs in Railway dashboard under your service

## Local Development

Your local development remains unchanged:
```bash
cd backend
python manage.py runserver
```

Railway configuration only affects production deployment.

## Cost

- **Free tier**: 512MB RAM, $5 credit monthly
- **Pro tier**: $20/month for more resources
- **Database**: Included in free tier (small size)

## Next Steps

1. Deploy and test
2. Update domain name in settings.py
3. Configure custom domain (optional)
4. Set up CI/CD workflows (optional)