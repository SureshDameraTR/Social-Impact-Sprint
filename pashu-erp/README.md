# PashuRaksha ERP (ಪಶುರಕ್ಷ)

Livestock management platform for rural Indian farmers.

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+ with uv
- Node.js 22+ with pnpm (via NVM)

### Setup

```bash
# Start full stack (PostgreSQL + API + Mock backends)
docker compose up -d

# API available at http://localhost:8000/docs
# Mock backends at http://localhost:8001/docs
```

### Demo Credentials

All accounts use OTP `123456` (console provider):

| Role | Phone | Name |
|------|-------|------|
| Admin | +919900000001 | Deepak Kumar |
| Farmer | +919900000002 | Lakshmi Devi |
| Farmer | +919900000003 | Annapurna Gowda |
| Farmer | +919900000004 | Savitri Bai |
| Vet | +919900000005 | Dr. Ramesh |

### Packages

| Package | Path | Stack | Port |
|---------|------|-------|------|
| API | `packages/api/` | FastAPI (28 routers, 25 models) | 8000 |
| Admin | `packages/admin/` | Next.js 14 + Refine + MUI (16 pages) | 3000 |
| Mobile | `packages/mobile/` | Expo 52 + React Native Paper (26 screens) | 8081 |
| Collection | `packages/collection/` | Vite + MUI PWA (6 pages) | 3001 |
| Vet | `packages/vet/` | Vite + MUI + Leaflet (5 pages) | 3002 |
| Mocks | `mocks/` | FastAPI (weather, registry, IoT, storage) | 8001 |

### Development

```bash
# API
cd packages/api
uv run ruff check app/          # Lint
uv run pytest tests/ -v         # Tests
uv run uvicorn app.main:app --port 8000

# Admin dashboard
cd packages/admin
pnpm install && pnpm dev        # http://localhost:3000

# Collection Centre
cd packages/collection
pnpm install && pnpm dev        # http://localhost:3001

# Vet Dashboard
cd packages/vet
pnpm install && pnpm dev        # http://localhost:3002

# Mobile
cd packages/mobile
pnpm install && npx expo start  # http://localhost:8081
```
