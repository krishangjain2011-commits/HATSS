# API Specification

## Authentication
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout

## Dashboard
GET /api/v1/dashboard

## Devices
GET /api/v1/devices
GET /api/v1/devices/{id}

## Scanner
POST /api/v1/scan
GET /api/v1/scans

## Conventions
- JSON responses
- Versioned endpoints
- Standard HTTP status codes
- Consistent error format
