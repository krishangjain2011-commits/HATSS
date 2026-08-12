# Render Manual Setup - Complete Step by Step

## Problem
Render is looking for `package.json` in `/opt/render/project/src/` but it's actually in `/opt/render/project/frontend/`

---

## SOLUTION: Delete and Recreate Services

The easiest fix is to **delete both services and create them fresh** with correct settings.

### Step 1: Delete Existing Services

1. Go to https://dashboard.render.com
2. **For hatss-frontend service**:
   - Click the service
   - Click **Settings** (scroll to bottom)
   - Click **Danger Zone** section
   - Click **Delete Service**
   - Confirm deletion

3. **For hatss-backend service**:
   - Click the service
   - Click **Settings** (scroll to bottom)
   - Click **Danger Zone** section
   - Click **Delete Service**
   - Confirm deletion

---

## Step 2: Create Frontend Service (Correct Way)

1. **Render Dashboard** → Click **"New +"** button
2. Select **"Static Site"** (NOT Web Service)
3. **Connect GitHub** to your repository if not already connected
4. **Select Repository**: `HATSS`
5. **Branch**: `feature/esp32-direct-integration`

6. **Configure:**
   - **Name**: `hatss-frontend`
   - **Root Directory**: `frontend` ← IMPORTANT!
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

7. **Add Environment Variables**:
   ```
   NODE_ENV = production
   VITE_API_URL = https://hatss-backend.onrender.com
   ```

8. Click **"Create Static Site"**

9. **Wait for build** (should take 1-2 minutes)

10. **Check Logs** for errors

---

## Step 3: Create Backend Service (Correct Way)

1. **Render Dashboard** → Click **"New +"** button
2. Select **"Web Service"** (NOT Static Site)
3. **Connect GitHub** to your repository
4. **Select Repository**: `HATSS`
5. **Branch**: `feature/esp32-direct-integration`

6. **Configure:**
   - **Name**: `hatss-backend`
   - **Runtime**: `Python`
   - **Root Directory**: `backend` ← IMPORTANT!
   - **Build Command**: `pip install -e . && pip install gunicorn`
   - **Start Command**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`

7. **Add Environment Variables**:
   ```
   HATSS_ENVIRONMENT = production
   HATSS_DEBUG = false
   HATSS_DOCS_ENABLED = false
   HATSS_CORS_ORIGINS = ["https://hatss-frontend.onrender.com"]
   HATSS_TRUSTED_HOSTS = ["hatss-backend.onrender.com","localhost"]
   POSTGRES_DB = hatss
   POSTGRES_USER = hatss
   ```

8. Click **"Create Web Service"**

9. **Wait for build** (should take 2-3 minutes)

10. **Check Logs** for errors

---

## Step 4: Verify Deployment

### Frontend Check:
- URL: `https://hatss-frontend.onrender.com`
- You should see the HATSS dashboard

### Backend Check:
- URL: `https://hatss-backend.onrender.com/api/v1/health`
- Should return JSON: `{"status":"ok"}`

### API Docs:
- URL: `https://hatss-backend.onrender.com/docs`
- Should show Swagger documentation

---

## If Frontend Still Shows npm Error

Do this **BEFORE creating the service**:

1. Make sure `package.json` exists in your local `frontend/` directory
2. Check the file contains valid JSON
3. Push to GitHub: `git push origin feature/esp32-direct-integration`
4. Then create the Render service

---

## If Backend Still Shows pip Error

Do this **BEFORE creating the service**:

1. Make sure `pyproject.toml` exists in your local `backend/` directory
2. Check that `backend/app/main.py` exists
3. Push to GitHub: `git push origin feature/esp32-direct-integration`
4. Then create the Render service

---

## Critical Settings Checklist

### Frontend Service MUST Have:
- [ ] Type: **Static Site**
- [ ] Root Directory: **`frontend`** (NOT blank, NOT `/`, NOT `./frontend`)
- [ ] Build Command: **`npm install && npm run build`**
- [ ] Publish Directory: **`dist`** (NOT `frontend/dist`, just `dist`)
- [ ] NO Docker settings
- [ ] Branch: **`feature/esp32-direct-integration`**

### Backend Service MUST Have:
- [ ] Type: **Web Service**
- [ ] Runtime: **Python** (NOT Docker)
- [ ] Root Directory: **`backend`** (NOT blank, NOT `/`)
- [ ] Build Command: **`pip install -e . && pip install gunicorn`**
- [ ] Start Command: **`gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`**
- [ ] NO Docker settings
- [ ] Branch: **`feature/esp32-direct-integration`**

---

## Why Services Need Deletion

When services are created with wrong settings, Render "remembers" them even after you edit. The safest fix is:

1. Delete the incorrectly configured service
2. Create a fresh service with correct settings
3. Everything works!

---

## Expected Timeline

- **Frontend Build**: 1-2 minutes
- **Backend Build**: 2-3 minutes
- **Total**: ~5 minutes for both

---

## Common Mistakes to Avoid

❌ **DON'T**:
- Leave Root Directory blank
- Set Root Directory to `/` or `./`
- Use `/frontend` or `/backend` with leading slash
- Mix up Static Site (frontend) and Web Service (backend)
- Keep Docker settings enabled

✅ **DO**:
- Set Root Directory to exactly: `frontend` or `backend`
- Use Static Site for frontend
- Use Web Service for backend
- Have NO Docker settings
- Verify settings match checklist above

---

## Support

If you still have issues after following these steps:

1. Check **Logs** tab on the service
2. Copy the full error message
3. Share it in: https://github.com/krishangjain2011-commits/HATSS/issues
4. Include screenshot of Render service settings

---

## It Should Work Now! ✅

Follow these steps exactly and your HATSS will deploy successfully to Render!
