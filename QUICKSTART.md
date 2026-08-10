# HATSS Hi + Face Recognition + Sensors - Quick Start

## What Was Done

✅ **Complete integration of HATSS Testing v1.0 features into HATSS Hi v0.1**

- Face recognition with MediaPipe (real-time facial landmark detection)
- ESP32 sensor support (fire, motion/PIR, gas)
- Intrusion detection and logging
- Live dashboard with new pages for face recognition and sensors
- Professional UI components with auto-refresh

---

## Before You Start

You'll need:
- Docker & Docker Compose installed
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)

Optional:
- `face_landmarker.task` model file (for full face recognition)

---

## Option 1: Run with Docker (Recommended)

```bash
cd e:\hatss_Hi\HATSS

# Start all services
docker-compose up --build

# Open in browser
# Frontend: http://localhost:5173
# Backend API Docs: http://localhost:8000/docs
```

That's it! The app will be running with:
- PostgreSQL database
- FastAPI backend with all new endpoints
- React frontend with new pages

---

## Option 2: Run Locally (Development)

### Backend
```bash
cd e:\hatss_Hi\HATSS\backend

# Create virtual environment (if needed)
py -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be at: `http://localhost:8000`

### Frontend
```bash
cd e:\hatss_Hi\HATSS\frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be at: `http://localhost:5173`

---

## New Pages in Dashboard

### 📸 Face Recognition (`#face`)
- Real-time face detection status
- Known persons counter
- Intrusions detected counter
- Recent intrusion image gallery

### 🔌 Sensors (`#sensors`)
- Fire sensor status (with pulsing animation when active)
- Motion/PIR sensor status
- Gas sensor status
- Last sensor update timestamp

---

## API Endpoints

### Face Recognition
```bash
# Get face status
curl http://localhost:8000/api/v1/face/status

# List known faces
curl http://localhost:8000/api/v1/face/known

# Get count of known faces
curl http://localhost:8000/api/v1/face/known/count
```

### Sensors
```bash
# Send sensor data from ESP32
curl -X POST http://localhost:8000/api/v1/sensors/data \
  -H "Content-Type: application/json" \
  -d '{"fire": false, "pir": true, "gas": false}'

# Get current sensor status
curl http://localhost:8000/api/v1/sensors/status

# Get alert status
curl http://localhost:8000/api/v1/sensors/alerts

# Get sensor metrics
curl http://localhost:8000/api/v1/sensors/metrics
```

### Intrusions
```bash
# Get recent intrusion images
curl http://localhost:8000/api/v1/intrusions/list?limit=6

# Get intrusion count
curl http://localhost:8000/api/v1/intrusions/count

# Get intrusion metrics
curl http://localhost:8000/api/v1/intrusions/metrics
```

---

## File Locations

### Data Storage
- **Known faces embeddings:** `backend/data/known_faces/*.npy`
- **Intrusion snapshots:** `backend/data/intruder_snaps/*.jpg`

### New Components
- **Backend services:** `backend/app/services/`
- **Frontend components:** `frontend/src/components/`

---

## Testing with Sample Data

### Test Sensor Submission
```bash
# Create a Python script: test_sensors.py
import requests
import json
import time

url = "http://localhost:8000/api/v1/sensors/data"
data = {"fire": False, "pir": True, "gas": False}

response = requests.post(url, json=data)
print(json.dumps(response.json(), indent=2))
```

Run it:
```bash
py test_sensors.py
```

### Monitor in Dashboard
1. Open http://localhost:5173
2. Click on "Sensors" in sidebar
3. You should see motion detector active (red dot, pulsing)

---

## Important Notes

### Face Recognition
- Uses **MediaPipe** for facial landmark detection
- Faces are stored as normalized **L2 embeddings** (32-bit floats)
- Matching uses **Euclidean distance** with 0.25 threshold
- Requires `face_landmarker.task` model file (not included, download from MediaPipe)

### Sensor Data
- Sensor state is **in-memory** (resets when backend restarts)
- ESP32 POSTs JSON with `fire`, `pir`, `gas` booleans
- Updates stored with timestamp

### Intrusion Logging
- Images stored as **JPEG** with Unix timestamp as filename
- 8-second **cooldown** between captures (prevents spam)
- Images accessible at `/intruder_snaps/{filename}`

### Frontend Updates
- Face status updates every **1 second**
- Sensor status updates every **1 second**
- Intrusion gallery updates every **3 seconds**

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

### Docker Issues
```bash
# Remove old containers
docker-compose down

# Rebuild everything
docker-compose up --build

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Frontend Not Connecting
- Check backend is running: `curl http://localhost:8000/api/v1/health/ready`
- Check CORS settings in `.env`
- Clear browser cache: Ctrl+Shift+Delete

### No Sensor Updates
- Verify endpoint: `curl http://localhost:8000/api/v1/sensors/status`
- Check POST format: `{"fire": bool, "pir": bool, "gas": bool}`
- Monitor backend logs for errors

---

## Next Steps

1. **Deploy with Docker**
   ```bash
   docker-compose up --build
   ```

2. **Test all endpoints** using API docs at `http://localhost:8000/docs`

3. **Integrate with ESP32** (when hardware ready)
   - Configure ESP32 IP/port in environment
   - Implement webhook receiver for video stream
   - Copy `face_landmarker.task` to backend root

4. **Optional: Enhance UI**
   - Add real-time video feed
   - Create known person registration form
   - Add notification system for alerts

---

## Documentation

- **INTEGRATION_STATUS.md** - Detailed integration report
- **VERIFICATION_CHECKLIST.md** - Complete verification checklist
- **MERGE_SUMMARY.txt** - Quick overview of changes

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     HATSS Hi Dashboard                       │
│  React 18 + TypeScript + Tailwind CSS                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Overview | Security | Processes | Network | Files |  │   │
│  │ Face Recognition | Sensors | AI Copilot             │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/REST
┌─────────────────────────┴───────────────────────────────────┐
│                  FastAPI Backend                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ /api/v1/                                             │   │
│  │  ├── health/     (System monitoring)                 │   │
│  │  ├── security/   (Defender, Sysmon)                 │   │
│  │  ├── system/     (CPU, Memory, Disk, Processes)     │   │
│  │  ├── network/    (Neighbors, TCP connections)       │   │
│  │  ├── files/      (Defender scan)                    │   │
│  │  ├── copilot/    (Ollama AI briefing)               │   │
│  │  ├── face/       (Face recognition) ✨ NEW          │   │
│  │  ├── sensors/    (ESP32 sensors) ✨ NEW             │   │
│  │  └── intrusions/ (Intrusion logging) ✨ NEW         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
    ┌───▼────┐       ┌───▼────┐       ┌───▼────┐
    │PostgreSQL        │ File System    │ ESP32
    │Database          │                │ Sensors
    │                  │ /data/         │ 
    │ tables,          │  ├── known_    │ POST
    │ events           │  │   faces/    │ {"fire": bool,
    │                  │  └── intruder_ │  "pir": bool,
    │                  │      snaps/    │  "gas": bool}
    └──────────────────┴────────────────┴────────────────┘
```

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f backend`
2. Review INTEGRATION_STATUS.md
3. Test endpoints manually with curl/Postman
4. Verify `.env` configuration

---

**Ready to go!** 🚀

Start with: `docker-compose up --build`
