# Project Foundation

## Purpose

This document describes the v0.1 HATSS software foundation. It establishes
repeatable local development, configuration boundaries, quality gates, and the
minimum operational checks required before cybersecurity features are added.

The foundation deliberately contains no authentication, user data, monitoring,
scanning, AI analysis, risk scoring, or hardware controls.

## Architecture

~~~text
Browser
  |
  v
React + Vite frontend
  |
  | /api/v1 via the development proxy
  v
FastAPI application
  |                  \
  |                   \ liveness check
  v                    \
SQLAlchemy + Alembic     PostgreSQL readiness check
  |
  v
PostgreSQL
~~~

The repository is a focused monorepo. Frontend and backend code live in
separate deployable directories, while Docker Compose provides the development
network and PostgreSQL instance. This keeps client dependencies isolated from
server dependencies and avoids introducing an unnecessary framework layer.

## Major decisions

### React, Vite, TypeScript, and Tailwind CSS

Vite gives the UI a fast local development server and production build. Strict
TypeScript is enabled so API and UI contracts are caught before runtime.
Tailwind CSS implements the documented dark-first design without inline CSS,
while the initial application shell presents an accessible dashboard using
clearly labelled illustrative data. No monitoring or security action is wired
to that interface yet.

### FastAPI with versioned routes

The backend exposes only two operational endpoints under /api/v1:

- /health/live confirms the API process can accept requests.
- /health/ready confirms the configured PostgreSQL server accepts connections.

Versioning begins now so feature routes can be added without later breaking
clients. Route handlers remain intentionally thin; future business logic
belongs in dedicated services, not endpoints.

### PostgreSQL, SQLAlchemy, and Alembic

PostgreSQL is the sole database in this milestone. SQLAlchemy 2 provides the
persistence boundary and Alembic owns schema history. The baseline migration
creates no domain tables; it only starts migration tracking. Future migrations
must be explicit and are never applied automatically when the API starts.

### Environment-only configuration

Configuration is read from environment variables. The committed .env.example
contains only placeholders, while .env is ignored by Git. Database passwords
are represented as secret values in server settings and never logged. CORS
uses an explicit origin list and trusted hosts are configurable, avoiding
wildcard development settings that could leak into deployment.

### Containers

Both application Dockerfiles use a development target and a production target.
The local Compose stack uses hot reload and a named PostgreSQL volume. The
database has a health check, and the API starts only after it is ready. The
frontend then waits for the API readiness health check. Migrations remain a
separate, deliberate command.

### Quality gates

The frontend runs ESLint, Prettier, Vitest, and its production build. The
backend runs Ruff, Black, Pytest, and an Alembic migration upgrade. GitHub
Actions runs these checks on pull requests and pushes to main with
read-only repository permissions.

## Usage

1. Copy .env.example to .env and replace the PostgreSQL password.
2. Run docker compose up --build.
3. Run docker compose exec backend alembic upgrade head.
4. Visit the frontend and call the liveness endpoint.
5. Run the local quality commands listed in README.md before opening a pull
   request.

## Manual verification

- Confirm the frontend is available at http://localhost:5173.
- Confirm GET /api/v1/health/live returns status ok.
- Confirm GET /api/v1/health/ready returns status ok while PostgreSQL runs.
- Stop PostgreSQL and confirm the readiness endpoint returns HTTP 503 while
  liveness remains available.
- Restart the stack and apply the Alembic baseline successfully.

## Known limitations

- Docker Desktop is required for the full local stack.
- The API has no authentication or domain endpoints.
- No domain models or tables exist yet.
- The production container targets are build-ready, but production networking,
  HTTPS termination, secrets management, backups, and monitoring remain
  deployment-specific work.
- The repository license text is still a placeholder.

## Next improvements

The next approved milestone is a separately designed authentication feature.
It should add a threat model, database migrations, input validation, tests,
and documentation before any dashboard or monitoring capability is built.
