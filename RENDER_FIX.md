# HATSS Render.com - Docker Error Fix

## Error
```
error: failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory
```

## Root Cause
Render detected Dockerfiles in your project and is trying to use Docker, but the Dockerfile paths are wrong for Render's Docker build system.

## Solution

### Option 1: Disable Docker in Render Dashboard (RECOMMENDED)

**For Each Service:**

1. **Open Render Dashboard** → Select Your Service

2. **Go to Settings**

3. **Scroll to "Build & Deploy"**

4. **Find and DISABLE**: 
   - ☐ "Use Docker" (uncheck this box)
   - OR look for "Dockerfile" field and leave it **BLANK**

5. **Set Build Settings**:
   
   **For Frontend Service:**
   - Build Command: `npm install --prefix frontend && npm run build --prefix frontend`
   - Publish Directory: `frontend/dist`
   - (Runtime should auto-detect as Node)

   **For Backend Service:**
   - Build Command: `pip install -e backend && pip install gunicorn`
   - Start Command: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`
   - Working Directory: `backend`
   - (Runtime should auto-detect as Python)

6. **Click "Save"**

7. **Click "Deploy" or "Manual Deploy"**

---

### Option 2: Create Root-Level Dockerfiles

If you prefer Docker, create these in the **root** of your project:

**File: `/Dockerfile.frontend`**
```dockerfile
FROM node:22-alpine AS dependencies
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

FROM dependencies AS build
COPY frontend ./
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
```

**File: `/Dockerfile.backend`**
```dockerfile
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY backend/pyproject.toml ./
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini ./

RUN pip install --upgrade pip && pip install .

EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]
```

Then in Render:
- **Frontend**: Set `Dockerfile` field to `Dockerfile.frontend`
- **Backend**: Set `Dockerfile` field to `Dockerfile.backend`

---

### Option 3: Delete Dockerfiles from Subdirectories

Remove Docker support completely:

```bash
rm frontend/Dockerfile
rm backend/Dockerfile
rm frontend/.dockerignore
rm backend/.dockerignore
git add -A
git commit -m "Remove Docker files for Render native build"
git push origin feature/esp32-direct-integration
```

Then use **Option 1** above.

---

## Recommended Path

**Option 1 (Disable Docker)** is the simplest for Render:

### Step-by-Step:

1. Go to https://dashboard.render.com

2. **For Frontend Service**:
   - Click on service name
   - Click "Settings"
   - Scroll down to "Build & Deploy"
   - **Uncheck** "Docker" (if present)
   - **Build Command**: `npm install --prefix frontend && npm run build --prefix frontend`
   - **Publish Directory**: `frontend/dist`
   - Click "Save"
   - Click "Manual Deploy" → "Deploy latest commit"

3. **For Backend Service**:
   - Click on service name
   - Click "Settings"
   - Scroll down to "Build & Deploy"
   - **Uncheck** "Docker" (if present)
   - **Build Command**: `pip install -e backend && pip install gunicorn`
   - **Start Command**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`
   - **Working Directory**: `backend`
   - Click "Save"
   - Click "Manual Deploy" → "Deploy latest commit"

4. **Wait** for builds to complete (~2-5 minutes)

5. **Check logs** for any errors:
   - Service → Logs

---

## Verify Deployment

After builds complete:

1. **Frontend**: Visit `https://hatss-frontend.onrender.com`
2. **Backend**: Visit `https://hatss-backend.onrender.com/api/v1/health`
3. **API Docs**: Visit `https://hatss-backend.onrender.com/docs`

---

## Troubleshooting

### Still Getting Docker Error?

1. **Clear Render Build Cache**:
   - Service → Settings → Danger Zone → "Clear Build Cache"
   - Then redeploy

2. **Check Branch**:
   - Make sure you're deploying from correct branch
   - Verify in Settings → Deploy → Branch

3. **Verify Settings Saved**:
   - After changing settings, wait 30 seconds
   - Refresh page
   - Verify settings are still there

### Build Fails with "npm: command not found"

- Make sure **Runtime** is set to **Node** (for frontend)
- Check **Node version** is 18+ in environment vars

### Build Fails with "python: command not found"

- Make sure **Runtime** is set to **Python** (for backend)
- Check **Python version** is 3.11 in settings

### "Cannot find module" Error

**For Frontend**:
- Check `npm install` is in build command
- Verify `package.json` exists in `frontend/` directory

**For Backend**:
- Check `pip install -e backend` in build command  
- Verify `pyproject.toml` exists in `backend/` directory

---

## Quick Check List

- [ ] Navigate to each service on Render Dashboard
- [ ] Go to Settings
- [ ] Verify Docker is **NOT** checked/enabled
- [ ] Set correct Build Command
- [ ] Set correct Start Command (backend only)
- [ ] Set Working Directory (backend: `backend`)
- [ ] Click Save
- [ ] Click Manual Deploy
- [ ] Wait for build (check logs)
- [ ] Test URLs

---

## Contact Support

If issue persists:

1. **Render Support**: https://render.com/support
2. **Check logs**: Service → Logs (full output)
3. **GitHub Issue**: https://github.com/krishangjain2011-commits/HATSS/issues

Share the full error message from Logs section.
