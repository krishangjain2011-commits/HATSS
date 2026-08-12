# Render Dashboard - Docker Settings Fix

## What You're Seeing

This is the **Advanced Settings** page in Render showing Docker-specific fields:
- Root Directory
- Registry Credential
- **Dockerfile Path** ← This is the problem
- Docker Build Context Directory
- Git Credentials
- Build Filters

---

## The Problem

**"Dockerfile Path"** is set to `./Dockerfile`

This tells Render to look for a Dockerfile in the root, but:
1. You deleted the Dockerfiles
2. You want to use Native Buildpacks instead

---

## The Fix

### Step 1: Click "Edit" Button
Next to **"Dockerfile Path"**, click the **Edit** button (pencil icon)

### Step 2: Clear the Field
The field currently shows: `./Dockerfile`

**Delete this text completely** - leave it BLANK

### Step 3: Save Changes
Click the **Save** button

### Step 4: Verify
After saving, the field should show empty/blank

---

## What Happens Next

Once "Dockerfile Path" is **blank**:
- Render switches to **Native Buildpacks** mode
- Uses your **Build Command** instead
- No more Docker errors!

---

## Complete Settings Needed

After clearing Dockerfile Path, make sure these are set:

### For Frontend Service:
```
Root Directory: frontend
Dockerfile Path: (LEAVE BLANK/EMPTY)
Build Command: npm install && npm run build
Publish Directory: dist
```

### For Backend Service:
```
Root Directory: backend
Dockerfile Path: (LEAVE BLANK/EMPTY)
Build Command: pip install -e . && pip install gunicorn
Start Command: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

---

## Then Deploy

1. Click **Manual Deploy** button (top right)
2. Select **Deploy latest commit**
3. Check logs for progress
4. Should complete without Docker errors!

---

## Why This Works

- **With Dockerfile Path set**: Render looks for Dockerfile (Docker build)
- **With Dockerfile Path blank**: Render uses Native Buildpacks (Node/Python detection)

Since you deleted the Dockerfiles, you MUST leave this blank to use native builds!

---

## Troubleshooting

### Still Seeing Docker Error?
1. Make sure you clicked **Save** after clearing Dockerfile Path
2. Wait 30 seconds
3. Refresh the page
4. Verify the field is now **empty**
5. Try **Manual Deploy** again

### Can't Find the "Edit" Button?
- Look for the **pencil icon** ✏️ next to "Dockerfile Path"
- Click that pencil to edit the field

### The Field Keeps Reappearing?
- Make sure you **saved** the changes
- Try clearing build cache: **Settings** → Scroll down → **Danger Zone** → **Clear Build Cache**
- Then redeploy

---

## Quick Checklist

- [ ] Found "Dockerfile Path" field
- [ ] Clicked "Edit" (pencil icon)
- [ ] Cleared the field (removed `./Dockerfile`)
- [ ] Clicked Save
- [ ] Field is now BLANK
- [ ] Clicked Manual Deploy
- [ ] Build is in progress

Done! ✅
