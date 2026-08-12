# HATSS

HATSS (House And Tech Security System) is a security-first platform that will
help people understand and respond to cybersecurity risks across their devices,
networks, and, later, their smart-home ecosystem.

The current milestone is the cybersecurity software foundation. The completed
hardware platform remains a future integration target; no hardware behavior is
implemented in this repository yet.

## Foundation scope

This v0.1 foundation provides:

- A React, TypeScript, Vite, and Tailwind CSS frontend.
- A FastAPI service with versioned infrastructure health endpoints.
- A live, read-only local-host telemetry endpoint and dashboard for CPU, memory,
  system disk, uptime, and accessible process metadata.
- Native Windows evidence integrations for Microsoft Defender, Sysmon, local
  network state, and user-requested Defender custom scans.
- PostgreSQL connectivity through SQLAlchemy and an Alembic migration baseline.
- Docker Compose for local development.
- Frontend and backend tests, linters, format checks, and GitHub Actions CI.

It intentionally does not provide authentication, user accounts, network device
scanning, automatic file actions, AI threat decisions, or hardware controls.
Network data is read-only; file scans require a specific folder and explicit
user request; the optional local AI briefing requires consent and cannot act on
the host. HATSS reports operational facts and source evidence, not a security
score.

## Architecture

~~~text
React + Vite UI
       |
       | versioned HTTP API
       v
FastAPI application
       |
       | SQLAlchemy + Alembic
       v
PostgreSQL
~~~

The frontend and backend are independent deployable units in one repository.
The backend keeps HTTP routing, configuration, persistence setup, and future
domain services separate so later security features can grow without changing
the foundation.

## Quick start

Prerequisites:

- Docker Desktop with Docker Compose v2
- Node.js 22+ and Python 3.11+ only if running services outside Docker

1. Copy the environment template.

   ~~~powershell
   Copy-Item .env.example .env
   ~~~

2. Set a unique local PostgreSQL password in .env.

3. Start the local stack.

   ~~~powershell
   docker compose up --build
   ~~~

4. In another terminal, apply the migration baseline.

   ~~~powershell
   docker compose exec backend alembic upgrade head
   ~~~

5. Open the frontend at http://localhost:5173 and verify the API at
   http://localhost:8000/api/v1/system/overview.

The local API documentation is available at http://localhost:8000/docs when
HATSS_DOCS_ENABLED is true. Keep it disabled in production.

## Local quality checks

~~~powershell
Set-Location frontend
npm.cmd ci
npm.cmd run lint
npm.cmd run format:check
npm.cmd run test:run
npm.cmd run build
~~~

~~~powershell
Set-Location ../backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m black --check .
.\.venv\Scripts\python -m pytest
~~~

See [the foundation guide](docs/21_PROJECT_FOUNDATION.md) for architecture
decisions, manual verification, constraints, and the next implementation steps.

## Roadmap

The planned development order is foundation, authentication, dashboard, device
monitoring, network monitoring, file security, AI-assisted analysis, cloud
services, and hardware integration. Each feature will be designed, tested, and
documented before the next one begins.

## Security and privacy

HATSS is designed around privacy, explicit user control, and secure defaults.
Do not commit .env files or credentials. Report vulnerabilities privately as
described in [SECURITY.md](SECURITY.md).

## License

The project license is currently a placeholder. It must be finalized before
any public release or distribution.
