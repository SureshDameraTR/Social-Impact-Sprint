## ADDED Requirements

### Requirement: Railway.app API deployment
The FastAPI backend SHALL be deployable to Railway.app free tier with a Postgres addon.

#### Scenario: API deploys to Railway
- **WHEN** the `packages/api/` directory is deployed to Railway
- **THEN** the API is accessible at a public URL with the Railway Postgres addon as the database

### Requirement: Vercel admin panel deployment
The Next.js admin panel SHALL be deployable to Vercel free tier via Git integration.

#### Scenario: Admin panel deploys to Vercel
- **WHEN** the `packages/admin/` directory is connected to Vercel
- **THEN** the admin panel is accessible at a public Vercel URL with environment variables pointing to the Railway API

### Requirement: Pre-demo warm-up
The deployment SHALL include a warm-up mechanism to prevent cold-start delays during the demo.

#### Scenario: API is warm before demo
- **WHEN** a warm-up curl is executed 5 minutes before the demo
- **THEN** the Railway API responds in < 1 second (no cold start)
