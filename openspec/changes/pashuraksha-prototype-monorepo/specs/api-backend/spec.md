## ADDED Requirements

### Requirement: FastAPI application factory with async database
The API SHALL use FastAPI with an async SQLAlchemy 2.0 engine (`asyncpg` driver), `async_sessionmaker` with `expire_on_commit=False`, and `pool_pre_ping=True`. Configuration SHALL use `pydantic-settings` loading from `.env` files.

#### Scenario: API starts and serves OpenAPI docs
- **WHEN** the API server starts
- **THEN** `GET /docs` returns the Swagger UI and `GET /openapi.json` returns the auto-generated OpenAPI 3.1 spec

#### Scenario: Database connection pool is healthy
- **WHEN** the API receives a request after a period of inactivity
- **THEN** the connection pool validates connections with `pool_pre_ping` before executing queries

### Requirement: 10 SQLAlchemy ORM models matching blueprint §7.1
The API SHALL define SQLAlchemy 2.0 async models for: `users`, `animals`, `health_events`, `vaccinations`, `yield_logs`, `milk_collection_centers`, `milk_collection_records`, `transactions`, `shg_groups`, `govt_schemes`. Column types and constraints SHALL match the blueprint ERD.

#### Scenario: All 10 models create tables
- **WHEN** Alembic migrations run against an empty database
- **THEN** all 10 tables exist with correct columns, types, foreign keys, and constraints

#### Scenario: Animal model includes Pashu Aadhaar field
- **WHEN** an animal record is created
- **THEN** the `pashu_aadhaar_id` column accepts a 12-digit INAPH ear tag identifier (nullable)

### Requirement: Alembic migration system
The API SHALL use Alembic for database migrations with all models imported in `env.py`.

#### Scenario: Initial migration creates all tables
- **WHEN** `alembic upgrade head` is run against an empty PostgreSQL 16 database
- **THEN** all 10 entity tables are created with correct schema

#### Scenario: Autogenerate detects model changes
- **WHEN** a developer modifies a SQLAlchemy model and runs `alembic revision --autogenerate`
- **THEN** Alembic generates a migration file reflecting the model changes

### Requirement: Separate Pydantic input/output models
The API SHALL define separate Pydantic v2 models for request bodies (Create/Update schemas) and response bodies (Read schemas). The API SHALL NOT use `response_model_exclude`.

#### Scenario: Create schema differs from read schema
- **WHEN** a `POST /v1/animals` request is made
- **THEN** the request body is validated against `AnimalCreate` (no `id`, no `created_at`) and the response uses `AnimalRead` (includes `id`, `created_at`)

### Requirement: Domain-based router organization
The API SHALL have one router file per domain module under `app/routers/`: `auth.py`, `animals.py`, `health.py`, `milk.py`, `finance.py`, `shg.py`, `schemes.py`, `admin.py`. All endpoints SHALL be under the `/v1/` prefix.

#### Scenario: API routes are organized by domain
- **WHEN** the OpenAPI spec is generated
- **THEN** endpoints are grouped by tags matching domain names (animals, health, milk, finance, shg, schemes, admin)
