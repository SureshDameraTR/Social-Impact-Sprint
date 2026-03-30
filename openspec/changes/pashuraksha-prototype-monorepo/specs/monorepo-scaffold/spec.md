## ADDED Requirements

### Requirement: Monorepo root structure with package boundaries
The monorepo SHALL have a `pashu-erp/` root directory containing `packages/api/`, `packages/admin/`, and `packages/mobile/` directories. Each package SHALL have its own dependency manifest (`pyproject.toml` or `package.json`). No package SHALL import code from another package directly.

#### Scenario: Root directory structure exists
- **WHEN** the monorepo is initialized
- **THEN** `pashu-erp/` contains `docker-compose.yml`, `.env.example`, `justfile`, `pnpm-workspace.yaml`, and `packages/` with `api/`, `admin/`, `mobile/` subdirectories

#### Scenario: Package isolation enforced
- **WHEN** a developer attempts to import from `packages/api` in `packages/mobile`
- **THEN** the import fails because packages have no cross-references in their dependency manifests

### Requirement: Docker Compose for local development
The monorepo SHALL include a `docker-compose.yml` that starts PostgreSQL 16 and the FastAPI backend.

#### Scenario: Local dev stack starts
- **WHEN** a developer runs `docker compose up`
- **THEN** PostgreSQL 16 is available on port 5432 and the API is available on port 8000

#### Scenario: Environment configuration
- **WHEN** `.env.example` is copied to `.env`
- **THEN** it contains `DATABASE_URL`, `SECRET_KEY`, `SARVAM_API_KEY`, and `CORS_ORIGINS` variables with documented defaults

### Requirement: Cross-language task runner
The monorepo SHALL include a `justfile` with tasks for common operations across all packages.

#### Scenario: Developer runs all tests
- **WHEN** a developer runs `just test`
- **THEN** pytest runs for `packages/api` and jest/vitest runs for `packages/admin` and `packages/mobile`

#### Scenario: Developer generates API client
- **WHEN** a developer runs `just generate-client`
- **THEN** `@hey-api/openapi-ts` reads the FastAPI OpenAPI spec and generates typed TypeScript client code
