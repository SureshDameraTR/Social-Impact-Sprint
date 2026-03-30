## ADDED Requirements

### Requirement: Docker Compose local development environment
The monorepo SHALL include a `docker-compose.yml` that starts all required services for local development.

#### Scenario: Full local stack starts
- **WHEN** `docker compose up` is run from the monorepo root
- **THEN** PostgreSQL 16 starts on port 5432, the FastAPI backend starts on port 8000 with hot-reload, and the database is ready to accept connections

#### Scenario: API auto-reloads on code changes
- **WHEN** a developer modifies a Python file in `packages/api/`
- **THEN** the FastAPI server automatically reloads (uvicorn `--reload`)

#### Scenario: Database data persists across restarts
- **WHEN** `docker compose down` and `docker compose up` are run
- **THEN** the PostgreSQL data volume persists and previous data is available

### Requirement: One-command seed
The monorepo SHALL support seeding the database with a single command.

#### Scenario: Developer seeds demo data
- **WHEN** `just seed` is run
- **THEN** the seed script executes against the running PostgreSQL and populates demo data
