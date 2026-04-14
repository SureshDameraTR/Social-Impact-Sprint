# API Package — Agent Instructions

FastAPI 0.115+ / SQLAlchemy 2.0 async / PostgreSQL 16 / Alembic

## Critical Rules

1. **Always async** — every DB call uses `async with get_session()`, never sync
2. **Always auth** — every router endpoint requires `Depends(get_current_user)` except `/v1/auth/*`
3. **Always paginate** — list endpoints return `{"data": [...], "total": int}`
4. **UUID PKs** — all tables use `uuid4` primary keys
5. **Soft delete** — set `deleted_at`, never hard delete. Filter with `.where(Model.deleted_at.is_(None))`
6. **Audit trail** — `created_at`, `updated_at` auto-set via `Base` class in `app/models/base.py`
7. **No `any` in Pydantic** — all schemas fully typed

## File Structure

See `../../WORKSPACE.md` for the complete file registry.

- **Models** (25): `app/models/` — SQLAlchemy ORM, one file per domain
- **Routers** (27): `app/routers/` — FastAPI endpoints, one file per domain
- **Schemas** (19): `app/schemas/` — Pydantic request/response models
- **Services** (13): `app/services/` — Business logic, external API clients
- **Middleware** (3): `app/middleware/` — auth, CSRF, request logging
- **Migrations** (9): `alembic/versions/` — sequential schema changes

## Adding a New Endpoint

```
1. Model:    app/models/<domain>.py     — SQLAlchemy table
2. Schema:   app/schemas/<domain>.py    — Pydantic In/Out models
3. Router:   app/routers/<domain>.py    — FastAPI route handlers
4. Mount:    app/main.py                — app.include_router(router, prefix="/v1/<domain>")
5. Migrate:  alembic revision --autogenerate -m "add <domain> table"
6. Test:     tests/test_<domain>.py     — pytest async tests
7. MANDATORY: Update ../../WORKSPACE.md — add rows to Models, Routers, Schemas tables
```

## Running

```bash
cd pashu-erp/packages/api
uv run ruff check app/                    # Lint
uv run pytest tests/ -v                   # Tests
uv run uvicorn app.main:app --port 8000   # Dev server
uv run alembic upgrade head               # Run migrations
```

## Key Patterns

- **Router → Service → Model**: Routers call services, services talk to DB via models
- **Error handling**: Raise `HTTPException` in routers, custom errors in `app/services/errors.py`
- **External services**: Weather, registry, IoT, storage — configured via env vars, mock at port 8001
- **OTP auth**: `app/services/otp/` — console provider logs to stdout in dev, Sarvam SMS in prod
- **Disease rules**: `app/services/disease_rules.py` — 55+ symptom→disease rules, 100% test coverage target
