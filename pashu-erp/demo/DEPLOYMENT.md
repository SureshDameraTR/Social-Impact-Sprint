# Deployment Notes

## Local Development Only
This prototype runs entirely on local Docker. No cloud deployment is configured.

### Running Locally
1. `docker compose up -d db` — Start Postgres
2. `just migrate` — Run migrations
3. `just seed` — Seed demo data
4. `just dev` — Start API at http://localhost:8000

### Why No Cloud?
- Work laptop restrictions prevent deploying to external services
- Local Docker provides identical functionality
- Demo will run from localhost during the April 27 scoping call
