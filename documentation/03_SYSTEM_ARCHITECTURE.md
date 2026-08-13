# System Architecture

## Overview
HATSS follows a layered, modular architecture to separate presentation, business logic,
AI services, persistence, and hardware integration.

```
React (UI)
    │
 REST API (FastAPI)
    │
Application Services
    │
 ├── Authentication
 ├── Monitoring
 ├── AI Engine
 ├── Threat Detection
 └── Notification Service
    │
Persistence Layer
(PostgreSQL / Redis)
    │
Operating System Interfaces
(psutil, scapy, watchdog, etc.)
```

## Design Principles
- Loose coupling
- High cohesion
- Dependency injection where practical
- Stateless APIs
- Clear module boundaries

## Future
- Desktop client
- Mobile client
- Cloud synchronization
- Hardware gateway
