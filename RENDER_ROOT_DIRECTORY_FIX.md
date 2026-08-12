# Render Error: "Could not read package.json"

## Error Message
```
npm error path /opt/render/project/src/package.json
npm error Could not read package.json: Error: ENOENT: no such file or directory
```

## Root Cause
Render is looking for `package.json` in the **wrong directory**.

It's looking in: `/opt/render/project/src/package.json`
But it should look in: `/opt/render/project/frontend/package.json`

---

## The Fix

### For Frontend Service ONLY:

1. **Open Render Dashboard**
2. **Click hatss-frontend service**
3. **Click Settings**
4. **Look for "Root Directory"** field
5. **Click Edit** (pencil icon ✏️)
6. **Set it to**: `frontend`
7. **Click Save**
8. **Manual Deploy** → **Deploy latest commit**

---

## Why This Works

When you set **Root Directory = `frontend`**:
- Render changes to `/opt/render/project/frontend/` directory
- It finds `package.json` at the correct location
- Build succeeds!

---

## Complete Frontend Settings

After this fix, your Frontend service should have:

```
Root Directory: frontend
Build Command: npm install && npm run build
Publish Directory: dist
Dockerfile Path: (BLANK/EMPTY)
Environment Variables:
  NODE_ENV = production
  VITE_API_URL = https://hatss-backend.onrender.com
```

---

## Backend Service (Should Already Be Correct)

Your Backend service should have:

```
Root Directory: backend
Build Command: pip install -e . && pip install gunicorn
Start Command: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
Dockerfile Path: (BLANK/EMPTY)
```

---

## Step-by-Step Screenshots

### Step 1: Click Settings
On Frontend Service page, click **Settings** tab

### Step 2: Find Root Directory
Scroll down in Settings, look for **"Root Directory"** field

### Step 3: Edit It
Click the **Edit** button (pencil icon ✏️) next to Root Directory

### Step 4: Type "frontend"
Clear any existing value and type: `frontend`

### Step 5: Save
Click **Save** button

### Step 6: Deploy
Click **Manual Deploy** → **Deploy latest commit**

---

## Expected Result

After setting `Root Directory = frontend`:
- Render will look in `/opt/render/project/frontend/`
- Find `package.json` ✓
- Install dependencies ✓
- Run build ✓
- No more npm errors! ✓

---

## Troubleshooting

### Still Getting Same Error?
1. Make sure you **saved** the Root Directory change
2. Wait 30 seconds
3. Refresh the page
4. Verify **Root Directory** now shows `frontend`
5. Try **Manual Deploy** again

### Root Directory Field Won't Save?
- Click **Edit** again
- Make sure field shows: `frontend` (not `./frontend` or `/frontend`)
- Click Save
- Should say "Settings updated"

### Build Still Fails?
- Check **Logs** tab for the full error message
- Common issues:
  - `node_modules` not installed → Check `npm install` in Build Command
  - Wrong working directory → Verify Root Directory is `frontend`
  - Missing env vars → Check Environment Variables tab

---

## Quick Checklist for Frontend

- [ ] Go to hatss-frontend service
- [ ] Click Settings
- [ ] Find "Root Directory" field
- [ ] Click Edit (pencil icon)
- [ ] Set value to: `frontend`
- [ ] Click Save
- [ ] Verify it now shows: `frontend`
- [ ] Click Manual Deploy
- [ ] Select "Deploy latest commit"
- [ ] Monitor Logs for success

---

## It Should Work Now! ✅

Once you set `Root Directory = frontend`, the npm error will be fixed and your frontend will deploy successfully.
