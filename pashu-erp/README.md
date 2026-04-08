# PashuRaksha ERP (ಪಶುರಕ್ಷ)

Livestock management platform for rural Indian farmers.

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+ with uv
- Node.js 20+ with pnpm
- just (task runner): `brew install just` or `cargo install just`

### Setup

```bash
# Start Postgres
docker compose up -d db

# Install API dependencies
cd packages/api && uv sync

# Run migrations
just migrate

# Seed demo data
just seed

# Start API server
just dev
# API available at http://localhost:8000/docs
```

### Demo Credentials
- Admin: +919900000001 / OTP: 123456
- Farmer (Lakshmi): +919900000002 / OTP: 123456
- Farmer (Annapurna): +919900000003 / OTP: 123456
- Farmer (Savitri): +919900000004 / OTP: 123456

### Packages
- `packages/api/` — FastAPI backend (21 routers, 19 models)
- `packages/mobile/` — Expo React Native app (26 screens)
- `packages/admin/` — Next.js + Refine admin dashboard (10 pages)
