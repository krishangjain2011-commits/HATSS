# HATSS - Complete Application Summary

## Project Overview

**HATSS (Home Automated Threat Security System)** is a comprehensive home security platform that combines:
- Real-time sensor monitoring (fire, motion, gas, water level)
- AI-powered facial recognition (YOLOv8)
- Network monitoring and analysis
- System health tracking
- ESP32 microcontroller integration
- Web-based dashboard with real-time updates

**Version**: 0.1.0  
**Repository**: https://github.com/krishangjain2011-commits/HATSS  
**Current Branch**: feature/esp32-direct-integration

---

## Application Architecture

### Frontend Stack
- **Framework**: React 19.0.0 with TypeScript 5.8.3
- **Build Tool**: Vite 7.0.0
- **Styling**: Tailwind CSS 4.1.0
- **Port**: 5173 (development)
- **Key Features**:
  - Real-time dashboard with 10ms sensor polling
  - Dark/Light theme support
  - Responsive design (mobile & desktop)
  - Live sensor monitoring
  - Face recognition interface
  - Intruder gallery
  - Network safety summary
  - System health overview

### Backend Stack
- **Framework**: FastAPI 0.115.x (async Python)
- **Server**: Uvicorn 0.34.x
- **Port**: 8000 (development)
- **Language**: Python 3.11+
- **Database**: PostgreSQL (psycopg3) / SQLite (dev)
- **Key Features**:
  - 9 asynchronous API endpoints
  - ESP32 proxy endpoint for CORS bypass
  - Face recognition service (YOLOv8 + multi-feature embeddings)
  - Sensor data aggregation
  - Real-time alerts
  - Database migrations (Alembic)

### Hardware Stack
- **Microcontroller**: ESP32 DevKit v1
- **Programming**: Arduino C++
- **WiFi**: Dual mode (Station + AP)
- **Sensors**:
  - IR Motion Sensor (GPIO 27)
  - Flame Detector (GPIO 32)
  - MQ2 Gas Sensor (GPIO 33)
  - Water Level Sensor (GPIO 34)
  - Buzzer (GPIO 25, PWM)
  - 0.96" OLED Display (I2C)

---

## Key Features Implemented

### 1. Real-Time Sensor Monitoring
- **Water Level**: 0-100% with color-coded alerts (>75% threshold)
- **Air Quality**: MQ2 rating 1-10 scale
- **Fire Detection**: Flame sensor monitoring
- **Motion Detection**: IR motion sensor (PIR)
- **Gas Detection**: MQ2 gas sensor
- **Update Interval**: 10ms for smooth real-time display

### 2. Face Recognition System
- **Model**: YOLOv8 (nano version, auto-downloads ~6.3MB)
- **Detection**: Real-time face detection in video stream
- **Embeddings**: Multi-feature extraction
  - Sobel edge features
  - Histogram of Oriented Gradients (HOG)
  - LAB color histograms
  - Spatial edge analysis
  - Laplacian-based features
- **Matching Threshold**: 0.35 Euclidean distance
- **Known Faces Dir**: `backend/data/known_faces/`
- **Intruder Snaps Dir**: `backend/data/intruder_snaps/`

### 3. ESP32 Integration
- **Access Point Mode**:
  - SSID: `HATSS_SECURITY_NET`
  - Password: `HATSS1234`
  - IP: `192.168.4.1`
  - Local API: `GET /api/sensors`
- **Data Fetching**:
  - **Tier 1**: Direct from ESP32 (10ms polling)
  - **Tier 2**: Backend proxy (fallback)
  - **Tier 3**: Stored backend data (offline)
- **Response Format**:
  ```json
  {
    "ir": false,
    "flame": false,
    "gas": false,
    "water": 45.5,
    "mq2_rating": 3,
    "buzzer": false,
    "muted": false,
    "raw_water": 2500
  }
  ```

### 4. Network Monitoring
- **Status Display**: Simple "SAFE" or "CHECK" status
- **Safety Criteria**:
  - Neighbors < 50 entries = Safe
  - TCP Connections < 100 = Safe
- **Data Collected**:
  - Network neighbors (ARP table)
  - Active TCP connections
  - Process ownership info

### 5. System Health Monitoring
- **CPU Usage**: Percentage with logical core count
- **Memory Usage**: Percentage with available bytes
- **Disk Usage**: Percentage with free space
- **Running Processes**: Count and top consumers
- **Uptime**: Days, hours, boot time

### 6. Security Features
- **Defender Integration**: Windows Defender data
- **Sysmon Monitoring**: Windows event logs
- **Custom File Scan**: Defender custom scan capability
- **Intrusion Detection**: Intruder face capture and gallery

---

## API Endpoints

### Sensor Endpoints
```
GET  /api/v1/sensors/esp32/live          - Live ESP32 data (proxy)
GET  /api/v1/sensors/status               - Current sensor status
POST /api/v1/sensors/data                 - Receive ESP32 data
GET  /api/v1/sensors/alerts               - Current alerts
GET  /api/v1/sensors/metrics              - Sensor metrics
```

### Face Recognition Endpoints
```
GET  /api/v1/face/status                  - Face recognition status
POST /api/v1/face/capture                 - Capture face image
POST /api/v1/face/register                - Register known face
GET  /api/v1/face/known-faces             - List of known faces
GET  /api/v1/face/intruders               - Intruder detections
```

### System Endpoints
```
GET  /api/v1/system/overview              - System health
GET  /api/v1/system/security              - Defender/Sysmon status
GET  /api/v1/network/overview             - Network data
GET  /api/v1/health                       - API health check
```

---

## Directory Structure

```
HATSS/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── sensors.py
│   │   │   │   ├── face.py
│   │   │   │   ├── security.py
│   │   │   │   ├── system.py
│   │   │   │   ├── network.py
│   │   │   │   ├── intrusions.py
│   │   │   │   ├── file_security.py
│   │   │   │   ├── health.py
│   │   │   │   └── __init__.py
│   │   │   └── router.py
│   │   ├── schemas/       (Pydantic models)
│   │   ├── services/      (Business logic)
│   │   ├── db/            (Database config)
│   │   ├── core/
│   │   │   └── config.py  (Environment config)
│   │   └── main.py        (Application factory)
│   ├── alembic/           (Database migrations)
│   ├── tests/             (Test suite)
│   ├── data/
│   │   ├── known_faces/   (Face embeddings)
│   │   └── intruder_snaps/(Captured images)
│   ├── pyproject.toml
│   ├── hatss.db           (SQLite dev database)
│   └── esp32_integration_code.ino
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DashboardPanel.tsx
│   │   │   ├── SensorMonitor.tsx
│   │   │   ├── FaceMonitor.tsx
│   │   │   ├── IntrusionGallery.tsx
│   │   │   ├── SystemHealth.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── DeviceTable.tsx
│   │   │   └── MetricCard.tsx
│   │   ├── pages/
│   │   │   └── ESP32Debug.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── documentation/         (Moved from docs/)
├── .env                   (Local - gitignored)
├── .env.example           (Template)
├── .gitignore
├── TECH_STACK.txt
├── TECH_STACK_SUMMARY.txt
├── APP_SUMMARY.md        (This file)
└── README.md
```

---

## Environment Configuration

### Required Variables (.env)
```
# Database
POSTGRES_DB=hatss
POSTGRES_USER=hatss
POSTGRES_PASSWORD=123456789
POSTGRES_PORT=5432

# Application
BACKEND_PORT=8000
FRONTEND_PORT=5173

# FastAPI
HATSS_ENVIRONMENT=development
HATSS_DEBUG=false
HATSS_DOCS_ENABLED=true
HATSS_DATABASE_HOST=localhost
HATSS_DATABASE_PORT=5432
HATSS_CORS_ORIGINS=["http://localhost:5173"]
HATSS_TRUSTED_HOSTS=["localhost","127.0.0.1","testserver","backend"]

# ESP32
ESP32_AP_SSID=HATSS_SECURITY_NET
ESP32_AP_PASSWORD=HATSS1234
ESP32_API_URL=http://192.168.4.1

# Features
ENABLE_FACE_RECOGNITION=true
ENABLE_MOTION_DETECTION=true
ENABLE_FIRE_DETECTION=true
ENABLE_GAS_DETECTION=true
ENABLE_WATER_LEVEL_MONITORING=true
ENABLE_INTRUSION_DETECTION=true
ENABLE_OLED_DISPLAY=true
ENABLE_WIFI=true
ENABLE_BACKEND_SYNC=true

# Thresholds
WATER_LEVEL_THRESHOLD=75
MQ2_THRESHOLD=2200
FACE_RECOGNITION_THRESHOLD=0.35
ALERT_COOLDOWN=8
SENSOR_POLL_INTERVAL=10
```

---

## Development Workflow

### Starting the Application
```bash
# Terminal 1 - Frontend
cd frontend
npm run dev
# Runs on http://localhost:5173

# Terminal 2 - Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Runs on http://localhost:8000

# Terminal 3 - ESP32 (Optional - separate Arduino IDE)
# Upload esp32_integration_code.ino to ESP32
# Connect to HATSS_SECURITY_NET hotspot
```

### Building for Production
```bash
# Frontend
npm run build        # Creates dist/ folder
npm run preview      # Preview production build

# Backend
python -m pip install -e .  # Install package
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### Testing
```bash
# Frontend
npm run test         # Run Vitest
npm run test:run     # Single run

# Backend
pytest               # Run pytest suite
```

### Code Quality
```bash
# Frontend
npm run lint         # ESLint
npm run format:check # Prettier check
npm run format:write # Format code

# Backend
black .              # Format code
ruff check .         # Linting
```

---

## Data Flow Architecture

### Sensor Data Flow
```
ESP32 Sensors (10ms)
    ↓
ESP32 Local API (192.168.4.1/api/sensors)
    ↓
Frontend fetch (10ms polling)
    ├─→ Direct to 192.168.4.1 (Primary)
    ├─→ Backend proxy /api/v1/sensors/esp32/live (Fallback)
    └─→ Stored /api/v1/sensors/status (Offline)
    ↓
UI Update (Smooth real-time)
```

### Face Recognition Flow
```
Camera Feed (30fps via OpenCV)
    ↓
YOLOv8 Face Detection
    ↓
Multi-Feature Embedding Extraction
    ↓
Known Face Matching (threshold: 0.35)
    ├─→ Match found: Known person
    └─→ No match: Intruder detection
    ↓
Capture intruder image
Alert + Store in database
```

### Network Data Flow
```
Windows Networking Stack
    ├─→ Neighbor Entries (ARP table)
    └─→ TCP Connections (netstat)
    ↓
Backend API Aggregation
    ↓
Frontend Display
    ├─→ Safety Status (SAFE/CHECK)
    └─→ Thresholds: Neighbors < 50, TCP < 100
```

---

## Performance Metrics

### Frontend
- **Build Time**: ~2-3 seconds (Vite)
- **Dev Server Startup**: <1 second
- **Hot Reload**: <100ms
- **Sensor Data Latency**: 10ms polling
- **Real-time Updates**: 100 Hz

### Backend
- **Endpoint Response**: <50ms (excluding I/O)
- **Database Query**: <100ms (with indexes)
- **ESP32 Proxy**: <100ms round trip
- **Async Processing**: Non-blocking

### Hardware
- **Sensor Sampling**: 10ms cycle
- **WiFi Latency**: 5-50ms
- **Display Update**: 150ms (OLED)
- **Buzzer Response**: <10ms

---

## Known Issues & Limitations

1. **PostgreSQL Optional**: Database currently optional (dev uses SQLite)
2. **Face Recognition**: Requires good lighting and clear face image
3. **WiFi Range**: ESP32 max ~50 meters in open space
4. **Sensor Calibration**: IR sensor needs 60 seconds after power-on
5. **OLED Display**: Updates at 150ms for power saving (not critical path)

---

## Future Enhancements

### Short Term
- WebSocket for real-time push notifications
- Historical data chart visualization
- Custom alert thresholds via UI
- Multi-user support with authentication

### Medium Term
- Mobile app (React Native)
- Email/SMS alerts
- Cloud synchronization
- Machine learning anomaly detection

### Long Term
- Edge computing on ESP32
- Additional sensor types
- Advanced video analytics
- Integration with smart home systems

---

## Deployment Checklist

### Pre-Deployment
- [ ] Update .env with production values
- [ ] Set HATSS_ENVIRONMENT=production
- [ ] Disable HATSS_DEBUG=false
- [ ] Configure PostgreSQL connection
- [ ] Set CORS_ORIGINS to frontend domain
- [ ] Generate secure database password
- [ ] Test all endpoints

### Backend Deployment
- [ ] Build Docker image or virtual environment
- [ ] Run database migrations: `alembic upgrade head`
- [ ] Set up SSL/TLS certificates
- [ ] Configure reverse proxy (Nginx/Apache)
- [ ] Set up logging and monitoring
- [ ] Enable rate limiting

### Frontend Deployment
- [ ] Run `npm run build`
- [ ] Configure CDN for static assets
- [ ] Set API URL to backend domain
- [ ] Enable gzip compression
- [ ] Configure cache headers
- [ ] Test production build

### ESP32 Deployment
- [ ] Configure WiFi credentials for production network
- [ ] Update backend URL to production API
- [ ] Verify OTA update capability
- [ ] Test all sensor connections
- [ ] Monitor memory and performance

---

## Support & Documentation

### Local Documentation
- `TECH_STACK.txt` - Detailed tech stack breakdown
- `TECH_STACK_SUMMARY.txt` - Quick reference
- `ESP32_SETUP.md` - ESP32 hardware setup guide
- `documentation/` - Complete project documentation

### External Resources
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- Vite: https://vitejs.dev/
- Tailwind CSS: https://tailwindcss.com/
- YOLOv8: https://docs.ultralytics.com/
- ESP32: https://docs.espressif.com/

---

## Quick Start Script Template

```bash
#!/bin/bash
# Start HATSS Development Environment

# Set base directory
HATSS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting HATSS...${NC}"

# Start Backend
echo -e "${BLUE}[1/2] Starting Backend (port 8000)...${NC}"
cd "$HATSS_DIR/backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start Frontend
echo -e "${BLUE}[2/2] Starting Frontend (port 5173)...${NC}"
cd "$HATSS_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo -e "${GREEN}✓ HATSS Started!${NC}"
echo -e "${GREEN}Frontend: http://localhost:5173${NC}"
echo -e "${GREEN}Backend: http://localhost:8000${NC}"
echo -e "${GREEN}ESP32 (when connected): http://192.168.4.1${NC}"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
```

---

## Version Information

- **React**: 19.0.0
- **TypeScript**: 5.8.3
- **Vite**: 7.0.0
- **Tailwind CSS**: 4.1.0
- **FastAPI**: 0.115.x
- **Python**: 3.11+
- **Node.js**: 22.0.0 - 24.x
- **Arduino IDE**: 2.0+
- **ESP32 Core**: 2.0.0+

---

## Repository Information

- **GitHub**: https://github.com/krishangjain2011-commits/HATSS
- **Current Branch**: feature/esp32-direct-integration
- **Last Updated**: August 2026
- **License**: [To be specified]

---

## Contact & Support

For issues, questions, or contributions, please visit the GitHub repository.
