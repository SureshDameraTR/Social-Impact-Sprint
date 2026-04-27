# Contributing to PashuRaksha ERP

## Prerequisites

- **Docker** & Docker Compose
- **Node.js 22** via [NVM](https://github.com/nvm-sh/nvm)
- **Python 3.12+** with [uv](https://docs.astral.sh/uv/)
- **pnpm** (`npm install -g pnpm`)

## Getting Started

```bash
# Clone the repository
git clone <repo-url> && cd Social-Impact-Sprint/pashu-erp

# Start infrastructure (PostgreSQL + API + Mocks)
docker compose up -d

# API is at http://localhost:8000/docs
# Mock backends at http://localhost:8001/docs

# Admin dashboard
cd packages/admin
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && nvm use 22
pnpm install && pnpm dev
# http://localhost:3000

# Collection Centre PWA
cd packages/collection
pnpm install && pnpm dev
# http://localhost:3001

# Vet Dashboard
cd packages/vet
pnpm install && pnpm dev
# http://localhost:3002

# Mobile (Expo)
cd packages/mobile
pnpm install && npx expo start
# http://localhost:8081
```

## Development Workflow

1. Create a feature branch from `main`
2. Make your changes
3. Run quality gates (see below)
4. Submit a pull request

## Code Standards

- **Python**: `ruff` for linting/formatting, async everywhere, type hints on public APIs
- **TypeScript**: strict mode, no `any`, MUI theme tokens (not raw colors)
- **API responses**: list endpoints return `{ data: [], total: int }`
- **Auth**: every router endpoint requires `Depends(get_current_user)` (except `/v1/auth/*`)
- **Database**: UUID primary keys, soft delete (`deleted_at`), audit trail (`created_at`, `updated_at`)
- **No cross-package imports** -- each package is self-contained

## Testing

Run these before submitting a PR:

```bash
# API
cd packages/api
uv run ruff check app/
uv run pytest tests/ -v

# Admin
cd packages/admin
pnpm install && npx next build

# Collection / Vet
cd packages/collection && npx vite build
cd packages/vet && npx vite build
```

## Demo Credentials

All accounts use OTP `123456` (console provider):

| Role | Phone | Name |
|------|-------|------|
| Admin | +919900000001 | Deepak Kumar |
| Farmer | +919900000002 | Lakshmi Devi |
| Farmer | +919900000003 | Annapurna Gowda |
| Farmer | +919900000004 | Savitri Bai |
| Vet | +919900000005 | Dr. Ramesh |
