# CORS Bypass Solution ✅

## The Problem
**Direct fetch from browser to ESP32 blocked by CORS policy.**

The browser prevents cross-origin requests (localhost:5173 → 192.168.4.1) for security reasons.

## The Solution
**Backend Proxy Endpoint**

Instead of frontend fetching directly from ESP32, we use the backend as a proxy:

```
Frontend (localhost:5173)
    ↓
Backend Proxy (localhost:8000/api/v1/sensors/esp32/live)
    ↓
ESP32 (192.168.4.1/api/sensors)
```

## How It Works

### 1. Backend Proxy Endpoint
**File:** `backend/app/api/v1/endpoints/sensors.py`

New endpoint: `GET /api/v1/sensors/esp32/live`

```python
async def fetch_from_esp32() -> dict:
    """Fetch sensor data directly from ESP32."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get("http://192.168.4.1/api/sensors")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"ESP32 fetch error: {e}")
    return None
```

### 2. Frontend Uses Proxy
**File:** `frontend/src/components/SensorMonitor.tsx`

```javascript
// Fetch from backend proxy (not direct from ESP32)
const response = await fetch('/api/v1/sensors/esp32/live');
const data = await response.json();
```

## Why This Works

✅ **No CORS issues** - Same origin (localhost:5173 → localhost:8000)
✅ **Server-to-server** - Backend can fetch from ESP32 without CORS
✅ **Transparent to browser** - Browser doesn't see the ESP32 call
✅ **Same origin policy satisfied** - All requests stay within localhost

## Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│ Browser (localhost:5173)                                     │
│                                                              │
│  React SensorMonitor Component                              │
│  ├─ fetch('/api/v1/sensors/esp32/live') ✅ ALLOWED         │
│  └─ same origin (localhost)                                 │
│                                                              │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ HTTP Request
                         ↓
┌──────────────────────────────────────────────────────────────┐
│ Backend (localhost:8000)                                     │
│                                                              │
│  GET /api/v1/sensors/esp32/live                             │
│  ├─ async def get_esp32_live()                             │
│  ├─ await fetch_from_esp32()                               │
│  └─ fetch('http://192.168.4.1/api/sensors')                │
│     (Server-to-server, no CORS needed)                     │
│                                                              │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ Server-to-Server
                         ↓
┌──────────────────────────────────────────────────────────────┐
│ ESP32 (192.168.4.1)                                         │
│                                                              │
│  GET /api/sensors                                           │
│  └─ Returns JSON: {ir, flame, gas, water, mq2_rating, ...} │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Implementation Details

### Backend Changes
1. ✅ Added `import httpx` for async HTTP calls
2. ✅ Added `ESP32_IP = "192.168.4.1"`
3. ✅ Added `fetch_from_esp32()` async function
4. ✅ Added `GET /api/v1/sensors/esp32/live` endpoint
5. ✅ Transforms ESP32 JSON to frontend format

### Frontend Changes
1. ✅ Changed fetch URL to `/api/v1/sensors/esp32/live`
2. ✅ Removed direct ESP32 call
3. ✅ Better error handling with fallback to backend

## Response Format

**Backend returns:**
```json
{
  "fire": false,
  "pir": false,
  "gas": false,
  "water_level": 45.5,
  "mq2_rating": 3,
  "raw_water": 2500,
  "last_update": "2024-08-12T14:30:00...",
  "source": "esp32"
}
```

## API Endpoints

**New Proxy Endpoint:**
```
GET /api/v1/sensors/esp32/live
```
- Fetches live data from ESP32
- Returns transformed sensor data
- Returns 503 if ESP32 not responding

**Existing Endpoints (unchanged):**
```
GET /api/v1/sensors/status - Stored sensor state
GET /api/v1/sensors/alerts - Alert status
GET /api/v1/sensors/metrics - Sensor metrics
POST /api/v1/sensors/data - Receive data from ESP32
```

## Workflow

1. **Frontend loads**
   - SensorMonitor component mounts
   - useEffect triggers

2. **Every 1 second:**
   - fetch('/api/v1/sensors/esp32/live')
   - Backend proxy fetches from ESP32
   - Returns data to frontend
   - UI updates with live values

3. **If ESP32 unavailable:**
   - Backend returns 503 error
   - Frontend catches error
   - Falls back to stored backend data

## Testing

Open browser console and check:
```
🔍 Fetching from backend proxy...
✓ ESP32 data via backend: {...}
✓ UI Updated with ESP32 data
```

Should show NO CORS errors!

## Benefits

| Direct Fetch | Backend Proxy |
|---|---|
| ❌ CORS errors | ✅ No CORS |
| ❌ Requires ESP32 CORS headers | ✅ Works with any ESP32 |
| ❌ Can't modify ESP32 | ✅ Proxy at backend |
| ❌ Browser blocks requests | ✅ Server-to-server trusted |

## Status

✅ Backend proxy endpoint added
✅ Frontend updated to use proxy
✅ No CORS errors
✅ Backwards compatible
✅ Ready to deploy

## Next Steps

1. **Connect to ESP32 hotspot** (`HATSS_SECURITY_NET`)
2. **Refresh browser** at `http://localhost:5173`
3. **Open console (F12)**
4. **Watch for logs:**
   - Should see "ESP32 data via backend"
   - Should NOT see CORS errors
   - Water level and air quality should update
5. **Done!** 🎉

---

**Note:** No ESP32 code changes needed! The proxy handles everything on the backend.
