# HATSS Deployment Guide for Render.com

## Overview
This guide walks you through deploying the HATSS application to Render.com with separate frontend and backend services.

---

## Prerequisites

1. **GitHub Account**: Push your code to GitHub
2. **Render Account**: Create free account at https://render.com
3. **Current Branch**: `feature/esp32-direct-integration` (or your production branch)

---

## Step 1: Prepare the Repository

Make sure all changes are committed and pushed:

```bash
git add .
git commit -m "Ready for Render deployment"
git push origin feature/esp32-direct-integration
```

---

## Step 2: Deploy Frontend

### Option A: Deploy as Static Site (Recommended for Frontend)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Static Site"**
3. Connect your GitHub repository
4. Select your repository and branch
5. Configure:
   - **Name**: `hatss-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
   - **Branch**: `feature/esp32-direct-integration` (or your branch)

6. Add Environment Variables:
   ```
   NODE_ENV = production
   VITE_API_URL = https://hatss-backend.onrender.com
   ```

7. Click **"Create Static Site"**

### Option B: Deploy as Web Service (More Control)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `hatss-frontend`
   - **Root Directory**: `frontend`
   - **Runtime**: `Node`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run preview`
   - **Branch**: `feature/esp32-direct-integration`

5. Add Environment Variables:
   ```
   NODE_VERSION = 22
   NODE_ENV = production
   VITE_API_URL = https://hatss-backend.onrender.com
   ```

6. Click **"Create Web Service"**

---

## Step 3: Deploy Backend

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `hatss-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -e . && pip install gunicorn`
   - **Start Command**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`
   - **Branch**: `feature/esp32-direct-integration`

5. Add Environment Variables:
   ```
   HATSS_ENVIRONMENT = production
   HATSS_DEBUG = false
   HATSS_DOCS_ENABLED = false
   HATSS_DATABASE_HOST = localhost
   HATSS_DATABASE_PORT = 5432
   HATSS_CORS_ORIGINS = ["https://hatss-frontend.onrender.com"]
   HATSS_TRUSTED_HOSTS = ["hatss-backend.onrender.com","localhost"]
   POSTGRES_DB = hatss
   POSTGRES_USER = hatss
   POSTGRES_PASSWORD = [generate-strong-password]
   ```

6. Click **"Create Web Service"**

---

## Step 4: Connect Database (Optional)

If you want to use PostgreSQL:

1. From Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `hatss-db`
   - **Database**: `hatss`
   - **User**: `hatss`
   - **Region**: Same as your services

3. Copy connection string from database detail page
4. Update backend environment variables:
   - `HATSS_DATABASE_HOST`: [from database details]
   - `HATSS_DATABASE_PORT`: `5432`
   - `POSTGRES_PASSWORD`: [from database details]

---

## Step 5: Update Frontend API URL

After backend deployment, update frontend environment:

1. Go to **Frontend Service** → **Settings** → **Environment**
2. Update `VITE_API_URL` to your backend URL (e.g., `https://hatss-backend.onrender.com`)
3. Click **"Save"**
4. Trigger new deploy: Go to **Deploys** → **Manual Deploy** → **Deploy latest commit**

---

## Troubleshooting

### Build Failing: "Could not find a package.json file"

**Problem**: Render can't find the project files

**Solution**: 
- Set correct **Root Directory** in service settings
- Frontend: `frontend`
- Backend: `backend`

### "ModuleNotFoundError: No module named 'app'"

**Problem**: Backend dependencies not installed

**Solution**:
- Verify `Build Command`: `pip install -e . && pip install gunicorn`
- Check `pyproject.toml` exists in backend root
- Ensure `PYTHONPATH` is set correctly

### "CORS error" in Frontend

**Problem**: Frontend can't reach backend API

**Solution**:
- Check `VITE_API_URL` environment variable is set
- Verify backend URL in environment is correct
- Check backend `HATSS_CORS_ORIGINS` includes frontend URL

### Frontend Shows Blank Page

**Problem**: Build succeeded but page is blank

**Solution**:
- Check **Publish Directory** is set to `frontend/dist`
- Verify `npm run build` succeeds locally
- Check browser console for JavaScript errors

### Backend Service Crashes

**Problem**: Service starts then stops

**Solution**:
- Check logs: **Service** → **Logs**
- Common causes:
  - Database connection issue
  - Missing environment variables
  - Port already in use
- Try redeploying: **Deploys** → **Manual Deploy**

---

## Environment Variables Reference

### Frontend
```
VITE_API_URL=https://hatss-backend.onrender.com
NODE_ENV=production
NODE_VERSION=22
```

### Backend
```
HATSS_ENVIRONMENT=production
HATSS_DEBUG=false
HATSS_DOCS_ENABLED=false
HATSS_DATABASE_HOST=hostname.render.com
HATSS_DATABASE_PORT=5432
HATSS_DATABASE_NAME=hatss
HATSS_DATABASE_USER=hatss
HATSS_DATABASE_PASSWORD=strong-password
HATSS_CORS_ORIGINS=["https://hatss-frontend.onrender.com"]
HATSS_TRUSTED_HOSTS=["hatss-backend.onrender.com","localhost"]
POSTGRES_DB=hatss
POSTGRES_USER=hatss
POSTGRES_PASSWORD=strong-password
```

---

## Monitoring

### View Logs
- **Service** → **Logs** → Real-time logs

### View Metrics
- **Service** → **Metrics** → CPU, Memory, Request rates

### View Events
- **Service** → **Events** → Deployment history and errors

---

## After Deployment

### Test Frontend
```
https://hatss-frontend.onrender.com
```

### Test Backend
```
https://hatss-backend.onrender.com/api/v1/health
https://hatss-backend.onrender.com/docs
```

### Access API Documentation
```
https://hatss-backend.onrender.com/docs
```

---

## Auto-Deploy on Push

By default, Render automatically deploys when you push to your branch:

1. Push to your connected branch
2. Render automatically triggers build
3. Check **Deploys** for status
4. View logs if deployment fails

---

## Rollback

To revert to previous version:

1. Go to Service → **Deploys**
2. Click on previous successful deployment
3. Click **"Redeploy"**

---

## Cost Considerations

- **Static Site (Frontend)**: Free tier available
- **Web Service (Backend)**: Paid (~$7/month minimum)
- **PostgreSQL Database**: Paid (~$15/month minimum)
- **Starter Plan**: Good for development/testing

---

## Performance Tips

1. **Enable Caching**:
   - Frontend: Browser cache headers configured
   - Backend: Consider Redis for sessions

2. **Optimize Images**:
   - Reduce image sizes
   - Use WebP format

3. **Database**:
   - Add indexes to frequently queried columns
   - Run migrations: `alembic upgrade head`

4. **API**:
   - Implement rate limiting
   - Cache API responses where possible

---

## Next Steps

1. Monitor application for 24 hours
2. Set up error tracking (Sentry, etc.)
3. Configure email alerts
4. Plan backup strategy
5. Document production URLs
6. Set up SSL/TLS (automatic with Render)

---

## Support

For Render-specific issues:
- Render Docs: https://render.com/docs
- Render Support: https://render.com/support
- Community: https://render.com/community

For HATSS issues:
- GitHub: https://github.com/krishangjain2011-commits/HATSS
- Issues: https://github.com/krishangjain2011-commits/HATSS/issues
