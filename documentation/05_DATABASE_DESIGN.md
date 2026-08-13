# Database Design

## Primary Database
PostgreSQL

## Core Tables
- users
- devices
- alerts
- scans
- threats
- audit_logs
- refresh_tokens

## Guidelines
- UUID primary keys
- Foreign keys for relationships
- Soft delete where appropriate
- Created/updated timestamps
- Indexed frequently queried columns

Never store plaintext passwords or sensitive secrets.
