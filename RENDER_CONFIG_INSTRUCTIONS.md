# How to Fix Render Build - STEP BY STEP

## The Problem
Render is configured to use **Docker build**, but Dockerfiles don't exist in the repo anymore.

## The Solution
Change Render settings from **Docker** to **Native Buildpacks**.

---

## FRONTEND SERVICE FIX

### Step 1: Open Frontend Service
1. Go to https://dashboard.render.com
2. Click **hatss-frontend** service

### Step 2: Go to Settings
1. Click the **Settings** tab
2. Scroll down to **Build & Deploy** section

### Step 3: Change Build Type
Look for one of these:
- "Docker" checkbox → **UNCHECK it**
- "Dockerfile" field → **DELETE the value, leave BLANK**
- "Environment" or "Buildpack" settings

### Step 4: Set Correct Configuration

In **Build & Deploy** section, set:

**Build Command:**
```
npm install --prefix frontend && npm run build --prefix frontend
```

**Publish Directory:**
```
frontend/dist
```

**NO Docker or Dockerfile settings should be filled in**

### Step 5: Save
Click the **Save** button

### Step 6: Deploy
1. Click **Manual Deploy** button (top right)
2. Select **Deploy latest commit**
3. Wait for build to complete

---

## BACKEND SERVICE FIX

### Step 1: Open Backend Service
1. Go to https://dashboard.render.com
2. Click **hatss-backend** service

### Step 2: Go to Settings
1. Click the **Settings** tab
2. Scroll down to **Build & Deploy** section

### Step 3: Change Build Type
Look for one of these:
- "Docker" checkbox → **UNCHECK it**
- "Dockerfile" field → **DELETE the value, leave BLANK**
- "Environment" or "Buildpack" settings

### Step 4: Set Correct Configuration

In **Build & Deploy** section, set:

**Build Command:**
```
pip install -e backend && pip install gunicorn
```

**Start Command:**
```
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

**Working Directory:**
```
backend
```

**NO Docker or Dockerfile settings should be filled in**

### Step 5: Save
Click the **Save** button

### Step 6: Deploy
1. Click **Manual Deploy** button (top right)
2. Select **Deploy latest commit**
3. Wait for build to complete

---

## VERIFICATION

After both services deploy successfully:

### Frontend Check
- URL: https://hatss-frontend.onrender.com
- Should see the HATSS dashboard

### Backend Check
- URL: https://hatss-backend.onrender.com/api/v1/health
- Should see JSON response: `{"status":"ok"}`

### API Docs
- URL: https://hatss-backend.onrender.com/docs
- Should see Swagger API documentation

---

## If Still Getting Docker Error

**Clear Build Cache:**

1. Service → **Settings**
2. Scroll to bottom → **Danger Zone**
3. Click **"Clear Build Cache"**
4. Go back to Build & Deploy
5. Click **Manual Deploy** again

---

## Environment Variables Check

### Frontend Service - Environment Tab
```
NODE_ENV = production
VITE_API_URL = https://hatss-backend.onrender.com
```

### Backend Service - Environment Tab
```
HATSS_ENVIRONMENT = production
HATSS_DEBUG = false
HATSS_DOCS_ENABLED = false
HATSS_CORS_ORIGINS = ["https://hatss-frontend.onrender.com"]
HATSS_TRUSTED_HOSTS = ["hatss-backend.onrender.com","localhost"]
```

---

## Screenshots Help

If you're unsure, look for these UI elements in Render Dashboard:

1. **Service name** → Click it
2. **Settings tab** (not Deploys, not Logs)
3. Scroll down to find **Build & Deploy** section
4. Look for **Docker checkbox** or **Dockerfile field** → Remove/Uncheck
5. Look for **Build Command** field → Enter the command above
6. Click **Save**
7. Click **Manual Deploy**

---

## Common Issues

### "Still getting Docker error"
- Make sure you clicked **Save** after changing settings
- Wait 30 seconds
- Refresh page
- Verify Docker checkbox is **unchecked**
- Verify Dockerfile field is **BLANK**

### "Build Command not working"
- Make sure you're in **Build & Deploy** section
- Copy-paste the exact command (no typos)
- Click Save
- Deploy

### "Module not found"
- Make sure `npm install` or `pip install` is in Build Command
- Check package.json / pyproject.toml exists in correct directories

---

## Final Checklist

**Frontend Service:**
- [ ] No Docker checkbox checked
- [ ] Dockerfile field is BLANK
- [ ] Build Command set to: `npm install --prefix frontend && npm run build --prefix frontend`
- [ ] Publish Directory set to: `frontend/dist`
- [ ] Settings Saved
- [ ] Manual Deploy triggered

**Backend Service:**
- [ ] No Docker checkbox checked
- [ ] Dockerfile field is BLANK
- [ ] Build Command set to: `pip install -e backend && pip install gunicorn`
- [ ] Start Command set to: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`
- [ ] Working Directory set to: `backend`
- [ ] Settings Saved
- [ ] Manual Deploy triggered

---

Done! Both services should now build successfully without Docker. ✅
