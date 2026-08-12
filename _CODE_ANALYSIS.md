# HATSS Hi (v0.1) - Code Architecture Analysis

## 📊 Project Structure Overview

```
HATSS/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── main.py            # Application factory
│   │   ├── core/
│   │   │   └── config.py      # Environment-based settings
│   │   ├── db/
│   │   │   ├── base.py        # SQLAlchemy base
│   │   │   └── session.py     # Database session management
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py  # Route aggregator
│   │   │       └── endpoints/
│   │   │           ├── health.py        # /health/live, /health/ready
│   │   │           ├── system.py        # /system/overview
│   │   │           ├── security.py      # /security/* endpoints
│   │   │           ├── network.py       # /network/* endpoints
│   │   │           ├── file_security.py # /files/* endpoints
│   │   │           └── copilot.py       # /copilot/* endpoints
│   │   ├── services/
│   │   │   ├── system_monitor.py       # System telemetry
│   │   │   ├── windows_security.py     # Windows Defender integration
│   │   │   ├── windows_network.py      # Network monitoring
│   │   │   ├── file_security.py        # File scanning
│   │   │   └── copilot.py              # AI integration
│   │   └── schemas/
│   │       ├── health.py               # Health check schemas
│   │       ├── system.py               # System telemetry schemas
│   │       ├── security.py             # Security schemas
│   │       ├── network.py              # Network schemas
│   │       ├── file_security.py        # File security schemas
│   │       └── copilot.py              # Copilot schemas
│   ├── alembic/                # Database migrations
│   ├── tests/                  # Backend test suite
│   ├── Dockerfile             # Multi-stage Docker build
│   ├── pyproject.toml         # Python dependencies
│   └── alembic.ini            # Migration config
│
├── frontend/                   # React + TypeScript + Vite
│   ├── src/
│   │   ├── main.tsx           # Entry point
│   │   ├── App.tsx            # Main component (1000+ lines)
│   │   ├── components/
│   │   │   ├── Sidebar.tsx            # Navigation sidebar
│   │   │   ├── DashboardPanel.tsx     # Reusable card/panel
│   │   │   ├── MetricCard.tsx         # Metric display component
│   │   │   ├── SystemHealth.tsx       # Health visualization
│   │   │   └── DeviceTable.tsx        # Process/device table
│   │   ├── services/
│   │   │   └── api.ts                 # API client (type-safe)
│   │   ├── styles/
│   │   │   └── index.css              # Tailwind imports
│   │   └── test/
│   │       ├── App.test.tsx           # Component tests
│   │       └── setup.ts               # Test configuration
│   ├── Dockerfile             # Multi-stage Docker build
│   ├── vite.config.ts         # Vite build config
│   ├── package.json           # npm dependencies
│   ├── tsconfig.json          # TypeScript config
│   ├── eslint.config.js       # Linting rules
│   ├── prettier.config.mjs    # Code formatting
│   └── nginx.conf             # Production web server config
│
├── compose.yaml               # Docker Compose orchestration
├── .env.example               # Environment template
├── README.md                  # Main documentation
└── docs/                      # 21 documentation files
```

---

## 🔧 Backend Architecture

### 1. **FastAPI Application Factory** (`main.py`)

```python
def create_application() -> FastAPI:
    """Create the API with safe, environment-configured middleware."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.docs_enabled else None,
    )
    
    # Middleware: TrustedHostMiddleware
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)
    
    # Middleware: CORS
    app.add_middleware(CORSMiddleware, ...)
    
    # Routes
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app
```

**Key Features:**
- Environment-based configuration
- Optional Swagger docs (`/docs`)
- TrustedHost middleware (prevent spoofing)
- CORS middleware (controlled origins)
- Versioned API routing (`/api/v1`)

### 2. **Configuration Management** (`config.py`)

```python
class Settings(BaseSettings):
    """Runtime settings from environment variables."""
    
    # App
    app_name: str = "HATSS API"
    app_version: str = "0.1.0"
    environment: Literal["development", "test", "production"]
    debug: bool = False
    docs_enabled: bool = False
    api_v1_prefix: str = "/api/v1"
    
    # CORS & Security
    cors_origins: list[AnyHttpUrl]
    trusted_hosts: list[str]
    
    # AI (Ollama/Copilot)
    copilot_enabled: bool = False
    copilot_base_url: str = "http://127.0.0.1:11434"
    copilot_model: str = "llama3.2:3b"
    
    # Database
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "hatss"
    database_user: str = "hatss"
    database_password: SecretStr | None = None
```

**Key Features:**
- Environment variable binding (`HATSS_*` prefix)
- Type validation with Pydantic
- Secret masking for passwords
- Copilot/Ollama local AI support
- Production safety checks (no debug in prod)

### 3. **System Telemetry Service** (`system_monitor.py`)

Collects operational facts WITHOUT making threat verdicts:

```python
def get_system_overview() -> SystemOverview:
    """Produce a live, non-destructive snapshot of the host."""
    
    return SystemOverview(
        observed_at=datetime.now(UTC),
        host=HostSummary(
            hostname=socket.gethostname(),
            operating_system=_operating_system(),
            booted_at=_booted_at(),
            uptime_seconds=...,
        ),
        cpu=CpuSummary(
            usage_percent=_cpu_usage_percent(),
            physical_cores=os.cpu_count(),
            logical_cores=os.cpu_count(),
        ),
        memory=MemorySummary(
            total_bytes=...,
            available_bytes=...,
            used_bytes=...,
            usage_percent=...,
        ),
        disk=DiskSummary(
            total_bytes=...,
            used_bytes=...,
            free_bytes=...,
            usage_percent=...,
        ),
        running_processes=...,
        top_processes=[ProcessSummary(...), ...],
        process_collection_status="available",
    )
```

**Data Collected:**
- ✅ CPU metrics (usage, core count)
- ✅ Memory (total, available, used, percent)
- ✅ Disk (total, used, free, percent)
- ✅ Running process count
- ✅ Top 8 processes by memory
- ✅ System uptime & boot time
- ✅ OS information (version, build)
- ✅ Hostname

**Windows-specific:**
- Uses `GlobalMemoryStatusEx` for memory
- Uses `GetSystemTimes` for CPU
- Uses `tasklist.exe` for processes
- Reads Windows Registry for OS version

**Linux-specific:**
- Reads `/proc/meminfo` for memory
- Uses `os.getloadavg()` for CPU
- Reads `/proc` filesystem for processes

**Important:** NO threat scoring, NO process classification, NO automatic actions

### 4. **API Endpoints Structure**

#### Health Endpoints
```
GET /api/v1/health/live  - API process ready
GET /api/v1/health/ready - Database connectivity
```

#### System Telemetry
```
GET /api/v1/system/overview - CPU, memory, disk, processes, uptime
```

#### Security (Windows)
```
GET /api/v1/security/defender/overview
GET /api/v1/security/defender/detections
POST /api/v1/security/files/scan (start Defender scan)

GET /api/v1/security/sysmon/overview
GET /api/v1/security/sysmon/events
```

#### Network
```
GET /api/v1/network/overview
GET /api/v1/network/neighbors (ARP table)
GET /api/v1/network/tcp-connections
```

#### File Security
```
GET /api/v1/files/scan-capability
POST /api/v1/files/scan (request custom scan)
```

#### AI Copilot
```
GET /api/v1/copilot/status
POST /api/v1/copilot/brief (ask question)
```

---

## 🎨 Frontend Architecture

### 1. **Main React Component** (`App.tsx`)

**Structure:**
```
App Component
├── State Management
│   ├── route (hash-based navigation)
│   ├── theme (light/dark)
│   ├── overview (system telemetry)
│   ├── defender (Windows Defender data)
│   ├── sysmon (Windows event logs)
│   ├── network (network data)
│   ├── scanCapability (Defender scan ability)
│   ├── copilotStatus (AI availability)
│   └── error/loading states
├── Data Fetching
│   ├── loadOverview() - Refreshes every 10 seconds
│   ├── All endpoints called in parallel
│   └── AbortController for cleanup
├── Event Handlers
│   ├── handleStartScan()
│   ├── handleCopilotBrief()
│   ├── theme toggle
│   └── navigation
└── Page Rendering
    ├── #overview - System metrics & health
    ├── #security - Defender & Sysmon evidence
    ├── #processes - Running processes table
    ├── #network - Network neighbors & TCP connections
    ├── #files - File scanning controls
    └── #copilot - AI question/answer
```

**Key Features:**
- Hash-based routing (`window.location.hash`)
- 10-second auto-refresh interval
- Parallel API calls (Promise.all)
- AbortController for cleanup
- Light/dark theme support (localStorage persistence)
- Error state display
- Loading indicators

### 2. **Data Flow**

```
User opens browser
    ↓
App initializes state
    ↓
useEffect triggers loadOverview()
    ↓
Parallel API calls:
├─ getSystemOverview()
├─ getDefenderOverview()
├─ getSysmonOverview()
├─ getNetworkOverview()
├─ getDefenderScanCapability()
└─ getCopilotStatus()
    ↓
setState() updates all data
    ↓
Component re-renders with new data
    ↓
setInterval repeats every 10 seconds
    ↓
Navigation changed? Update route state
    ↓
Render appropriate page based on route
```

### 3. **UI Components**

| Component | Purpose |
|-----------|---------|
| **Sidebar** | Navigation with active state |
| **DashboardPanel** | Card container with title/description |
| **MetricCard** | Displays metric value + unit + status |
| **SystemHealth** | Health visualizations (progress bars) |
| **DeviceTable** | Table for processes/devices |

### 4. **API Client** (`api.ts`)

```typescript
// Type-safe API calls
export async function getSystemOverview(signal?: AbortSignal): Promise<SystemOverview>
export async function getDefenderOverview(signal?: AbortSignal): Promise<DefenderOverview>
export async function startDefenderScan(directory: string): Promise<DefenderScanAction>
export async function requestCopilotBrief(question: string): Promise<CopilotBrief>
```

**Features:**
- Full TypeScript support
- Abort signal for cleanup
- Error handling
- Response type safety

---

## 📡 Data Flow Architecture

### Telemetry Refresh Loop

```
Frontend (React)
    ↓
10-second interval
    ↓
loadOverview() called
    ↓
Promise.all([
    fetch('/api/v1/system/overview'),
    fetch('/api/v1/security/defender/overview'),
    fetch('/api/v1/security/sysmon/overview'),
    fetch('/api/v1/network/overview'),
    fetch('/api/v1/files/scan-capability'),
    fetch('/api/v1/copilot/status'),
])
    ↓
Backend (FastAPI)
    ├─ system_monitor.get_system_overview()
    ├─ windows_security.get_defender_overview()
    ├─ windows_network.get_network_overview()
    ├─ file_security.get_scan_capability()
    └─ copilot.get_status()
    ↓
Response JSON
    ↓
Frontend setState()
    ↓
Component re-render
    ↓
User sees updated data
```

---

## 🗄️ Database (PostgreSQL)

**Baseline Migration:**
- Creates migration tracking (no domain tables yet)
- Prepared for future authentication
- Future user data storage
- Future threat history logging

**Configuration:**
- Host: localhost:5432
- Database: hatss
- User: hatss
- Password: From environment

---

## 🐳 Docker Architecture

### Services in `compose.yaml`

```yaml
services:
  postgres:              # PostgreSQL database
    image: postgres:16
    ports: 5432:5432
    healthcheck: enabled
    volume: hatss_postgres (named volume)
    
  backend:               # FastAPI application
    build: backend/
    ports: 8000:8000
    environment: .env
    depends_on: postgres (health check)
    volumes: hot-reload
    
  frontend:              # React development server
    build: frontend/
    ports: 5173:5173
    environment: Vite config
    depends_on: nothing
    volumes: hot-reload
```

**Development Features:**
- Hot reload for both frontend and backend
- Named volume for database persistence
- Service health checks
- Automatic startup order

---

## 🔌 Integration Points

### Windows-Specific Integrations

1. **Microsoft Defender**
   - Reads WinRM/WMI for status
   - Queries Windows Registry
   - Requests custom scans
   - Returns detection history

2. **Sysmon**
   - Windows event log reader
   - Process creation events
   - Network connection events
   - File operations events

3. **Windows Network Stack**
   - ARP table (neighbors)
   - TCP connection state
   - Network interface info

### Future Integrations (Planned)

- ✋ Ollama/local AI (Copilot)
- ✋ Cloud synchronization
- ✋ Multi-platform support
- ✋ Hardware integrations

---

## 🔒 Security & Privacy Design

### Intentional Constraints

- ❌ NO automatic actions
- ❌ NO threat scoring
- ❌ NO file modification
- ❌ NO network scanning
- ❌ NO process classification
- ✅ Read-only operations
- ✅ Explicit user requests
- ✅ Evidence-based reporting

### Production Safety

- Development features disabled in production
- Debug mode prohibited in production
- CORS strictly configured
- TrustedHost validation
- Password secrets not logged
- `.env` files git-ignored

---

## 📊 Key Architectural Decisions

### 1. Monorepo Structure
- Frontend and backend in one repo
- Independent Docker images
- Shared documentation
- Unified versioning

### 2. Versioned API (`/api/v1`)
- Future-proof routing
- Breaking changes handled via versioning
- New versions don't break old clients

### 3. TypeScript Everywhere
- React: Full TypeScript with strict mode
- API: Pydantic for schema validation
- Type safety across frontend/backend boundary

### 4. Thin Route Handlers
- Routes delegate to services
- Services contain business logic
- Database/schemas isolated
- Clear separation of concerns

### 5. Read-Only Operations
- No automatic threat response
- No file modifications
- No network scanning
- No threat scoring
- Evidence reporting only

---

## 🔄 Development Workflow

### Local Setup
```bash
# 1. Copy environment
Copy-Item .env.example .env
# Set POSTGRES_PASSWORD in .env

# 2. Start stack
docker compose up --build

# 3. Apply migrations
docker compose exec backend alembic upgrade head

# 4. Access services
# Frontend: http://localhost:5173
# API: http://localhost:8000
# Docs: http://localhost:8000/docs (if enabled)
```

### Quality Checks

**Frontend:**
```bash
npm run lint
npm run format:check
npm run test:run
npm run build
```

**Backend:**
```bash
python -m ruff check .
python -m black --check .
python -m pytest
```

---

## 🎯 Integration Points with HATSS Testing

### What v0.1 Provides
- ✅ Modern FastAPI backend
- ✅ TypeScript React frontend
- ✅ Modular architecture
- ✅ Windows integrations (Defender, Sysmon, Network)
- ✅ Docker/CI-CD setup
- ✅ Professional UI/UX
- ✅ API versioning

### What v1.0 Testing Provides
- ✅ Face recognition engine
- ✅ ESP32 sensor integration
- ✅ Intrusion detection
- ✅ Emergency response
- ✅ Real-time video processing

### Merge Strategy
```
New HATSS Merged
├── Frontend (from v0.1)  ← Professional React UI
├── Backend Services (mixed)
│   ├── System telemetry (from v0.1)
│   ├── Windows integrations (from v0.1)
│   ├── Face recognition (from v1.0)
│   ├── Sensor monitoring (from v1.0)
│   └── Intrusion detection (from v1.0)
└── Infrastructure (from v0.1)
    ├── FastAPI
    ├── PostgreSQL
    ├── Docker Compose
    └── GitHub Actions CI/CD
```

---

## 📝 Notes for Merge

1. **Routes to Add**
   - `/api/v1/face/*` - Face recognition
   - `/api/v1/sensors/*` - Sensor telemetry
   - `/api/v1/intrusions/*` - Intrusion data

2. **Services to Integrate**
   - Face recognition engine
   - Camera/video processing
   - Sensor data collection
   - Intrusion detection logic

3. **UI Pages to Add**
   - Live face feed with HUD
   - Sensor dashboard
   - Intrusion alerts
   - Face registration form

4. **Database Models to Create**
   - Face embeddings
   - Intrusion records
   - Sensor history
   - User preferences

---

**Analysis Complete!** Ready for merge planning.
