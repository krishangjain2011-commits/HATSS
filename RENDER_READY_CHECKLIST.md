# HATSS - Render Deployment Ready Checklist

## ✅ FIXES APPLIED

### Code Fixes:
- [x] Added `gunicorn>=23.0,<24.0` to backend/pyproject.toml dependencies
- [x] Made ESP32_IP configurable via `HATSS_ESP32_IP` environment variable
- [x] Added `python-multipart` dependency for FastAPI form handling
- [x] Added `httpx` to main dependencies for ESP32 proxy
- [x] Updated render.yaml with database migrations in startCommand
- [x] Added database configuration to render.yaml environment variables
- [x] Updated CORS origins for Render domains in render.yaml
- [x] Updated .env.example with production settings

### Configuration Ready:
- [x] render.yaml fully configured for frontend + backend
- [x] Database section included (optional, can be provisioned separately)
- [x] All environment variables documented
- [x] Build and start commands correct
- [x] Root directories correct (cd backend for backend service)

---

## 🚀 ONE-GO DEPLOYMENT STEPS

### Step 1: Create Render Account & Connect GitHub
1. Go to https://render.com
2. Sign up or log in
3. Connect your GitHub account
4. Grant access to HATSS repository

### Step 2: Create PostgreSQL Database (Optional but Recommended)
1. **Render Dashboard** → **New +** → **PostgreSQL**
2. Configure:
   - **Name**: `hatss-postgres`
   - **Database**: `hatss`
   - **User**: `hatss`
   - **Region**: Your preferred region (e.g., Ohio)
3. Click **Create**
4. **Wait** for database to be ready (~2 minutes)
5. Copy connection details from database page

### Step 3: Create Backend Service
1. **Render Dashboard** → **New +** → **Web Service**
2. Connect GitHub repo: Select `HATSS` repository
3. **Configure:**
   - **Name**: `hatss-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3.11`
   - **Build Command**: `cd backend && pip install -e . && pip install gunicorn`
   - **Start Command**: `cd backend && alembic upgrade head && gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`
   - **Branch**: `feature/esp32-direct-integration` (or your production branch)

4. **Add Environment Variables** (click "Add Environment Variable"):
   ```
   HATSS_ENVIRONMENT = production
   HATSS_DEBUG = false
   HATSS_DOCS_ENABLED = false
   HATSS_DATABASE_HOST = (from PostgreSQL details)
   HATSS_DATABASE_PORT = 5432
   HATSS_DATABASE_NAME = hatss
   HATSS_DATABASE_USER = hatss
   HATSS_DATABASE_PASSWORD = (from PostgreSQL details)
   POSTGRES_DB = hatss
   POSTGRES_USER = hatss
   POSTGRES_PASSWORD = (from PostgreSQL details)
   HATSS_CORS_ORIGINS = ["https://hatss-frontend.onrender.com"]
   HATSS_TRUSTED_HOSTS = ["hatss-backend.onrender.com","localhost"]
   HATSS_ESP32_IP = 192.168.4.1
   ```

5. Click **Create Web Service**
6. **Wait** for build to complete (~3-5 minutes)
7. **Check Logs** for any errors
8. Copy backend URL (e.g., `https://hatss-backend.onrender.com`)

### Step 4: Create Frontend Service
1. **Render Dashboard** → **New +** → **Static Site**
2. Connect GitHub repo: Select `HATSS` repository
3. **Configure:**
   - **Name**: `hatss-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
   - **Branch**: `feature/esp32-direct-integration` (or your production branch)

4. **Add Environment Variables:**
   ```
   NODE_ENV = production
   VITE_API_URL = https://hatss-backend.onrender.com
   ```

5. Click **Create Static Site**
6. **Wait** for build to complete (~2-3 minutes)
7. **Check Logs** for any errors
8. Copy frontend URL (e.g., `https://hatss-frontend.onrender.com`)

### Step 5: Update Backend CORS (Now That Frontend URL is Known)
1. **Render Dashboard** → **hatss-backend service**
2. **Settings** → **Environment** section
3. Find `HATSS_CORS_ORIGINS` variable
4. **Click Edit** and update value to: `["https://hatss-frontend.onrender.com"]` (use actual URL)
5. Click **Save**
6. Click **Manual Deploy** → **Deploy latest commit**
7. **Wait** for redeploy to complete

---

## 🔍 VERIFICATION

### Test Frontend
- URL: `https://hatss-frontend.onrender.com`
- Expected: See HATSS dashboard interface

### Test Backend API
- URL: `https://hatss-backend.onrender.com/api/v1/health` (if endpoint exists)
- Or: `https://hatss-backend.onrender.com/docs`
- Expected: See API documentation

### Test Sensor Endpoint
- URL: `https://hatss-backend.onrender.com/api/v1/sensors/status`
- Expected: JSON response with sensor data

---

## ⚠️ IMPORTANT NOTES

### Database:
- If not using Render PostgreSQL, SQLite will be used (ephemeral - data lost on restart)
- For production, PostgreSQL is **strongly recommended**
- Database migrations run automatically on startup

### File Storage:
- Intruder snapshots and known faces stored in ephemeral file system
- **This means data is lost when the dyno restarts**
- For production: Set up Render Disk or external storage (S3, etc.)

### ESP32 Integration:
- ESP32 IP is configurable via `HATSS_ESP32_IP` environment variable
- If using Render's ESP32 integration: set the appropriate IP
- If not using ESP32: This is optional, app works without it

### Costs:
- **Frontend (Static Site)**: Free tier available
- **Backend (Web Service)**: Paid (~$7/month minimum)
- **PostgreSQL Database**: Paid (~$15/month minimum)
- **Total**: ~$22/month for production-ready setup

---

## 🆘 TROUBLESHOOTING

### Backend Build Fails
- Check **Logs** tab for error messages
- Common causes:
  - Missing Python dependencies (check pyproject.toml)
  - Database connection timeout (verify PostgreSQL is running)
  - Incorrect environment variables

### Frontend Build Fails
- Check **Logs** tab
- Common causes:
  - Missing npm dependencies (check package.json)
  - Incorrect Node version (should be 22+)
  - Build script error

### Services Don't Communicate
- Verify `HATSS_CORS_ORIGINS` includes frontend URL
- Verify `VITE_API_URL` in frontend points to backend URL
- Check browser console for CORS errors

### Database Connection Fails
- Verify PostgreSQL database is created and running
- Check all database environment variables are set correctly
- Verify database credentials match between Render PostgreSQL and env vars
- Test connection string format

---

## 📋 POST-DEPLOYMENT

### Recommended Setup:
1. **Enable auto-deploy**: Both services should auto-redeploy on GitHub push
2. **Monitor logs**: Regularly check Render logs for errors
3. **Set up alerts**: Configure email notifications for failures
4. **Backup database**: Regular PostgreSQL backups
5. **Monitor costs**: Track monthly spending on Render dashboard

### Optional Enhancements:
- Add health checks to services
- Set up log drain to external logging service
- Configure custom domain name
- Add SSL/TLS certificate (automatic with Render)
- Set up staging environment for testing

---

## ✅ FINAL CHECKLIST

Before you deploy, verify:

- [ ] All code changes committed and pushed
- [ ] Branch name correct in Render settings
- [ ] PostgreSQL database created and credentials copied
- [ ] Backend environment variables set correctly
- [ ] Frontend VITE_API_URL points to backend
- [ ] Build commands are exactly as shown above
- [ ] Start command includes database migration
- [ ] Root directories are set (`backend` and `frontend`)
- [ ] Runtimes are correct (Python 3.11 for backend, Node for frontend)

---

## 🎯 RESULT

Once complete, you'll have:
- ✅ Frontend running at `https://hatss-frontend.onrender.com`
- ✅ Backend API running at `https://hatss-backend.onrender.com`
- ✅ PostgreSQL database connected
- ✅ Real-time sensor monitoring
- ✅ Face recognition working
- ✅ ESP32 integration (if ESP32 available)
- ✅ All production security enabled
- ✅ Auto-scaling and monitoring

**Total deployment time: ~15-20 minutes**

Good luck! 🚀
