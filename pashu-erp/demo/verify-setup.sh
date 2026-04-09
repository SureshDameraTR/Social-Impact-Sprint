#!/bin/bash
# PashuRaksha Setup Verification
# Run after: docker compose up + migrate + seed
set -e

echo "PashuRaksha Setup Verification"
echo "================================="
echo ""
echo "WARNING: Using mock OTP (123456) - development mode only"

# 1. Check Docker
echo ""
echo "1. Docker services..."
docker compose ps --format "table {{.Service}}\t{{.Status}}" 2>/dev/null || echo "   WARNING: Docker not running or compose file not found"

# 2. Check Postgres
echo ""
echo "2. PostgreSQL..."
docker compose exec -T db psql -U pashu -d pashuraksha -c \
  "SELECT count(*) as table_count FROM information_schema.tables WHERE table_schema='public';" \
  2>/dev/null || echo "   WARNING: Cannot connect to Postgres"

# 3. Check seed data
echo ""
echo "3. Seed data..."
docker compose exec -T db psql -U pashu -d pashuraksha -c \
  "SELECT role, count(*) FROM users GROUP BY role ORDER BY role;" \
  2>/dev/null || echo "   WARNING: Cannot query users table"

docker compose exec -T db psql -U pashu -d pashuraksha -c \
  "SELECT species, count(*) FROM animals GROUP BY species ORDER BY species;" \
  2>/dev/null || echo "   WARNING: Cannot query animals table"

# 4. Check API health
echo ""
echo "4. API health..."
HEALTH=$(curl -sf http://localhost:8000/health 2>/dev/null)
if [ -n "$HEALTH" ]; then
    echo "   $HEALTH" | python3 -m json.tool 2>/dev/null || echo "   $HEALTH"
else
    echo "   WARNING: API not responding at http://localhost:8000"
fi

# 5. Check OpenAPI docs
echo ""
echo "5. OpenAPI spec..."
ENDPOINT_COUNT=$(curl -sf http://localhost:8000/openapi.json 2>/dev/null | \
  python3 -c "import sys,json; print(len(json.load(sys.stdin).get('paths',{})))" 2>/dev/null || echo "0")
echo "   Registered endpoints: $ENDPOINT_COUNT"

# 6. Quick auth smoke test
echo ""
echo "6. Auth smoke test..."
OTP_RESP=$(curl -sf -X POST http://localhost:8000/v1/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phone":"+919900000002"}' 2>/dev/null)
if echo "$OTP_RESP" | grep -q "OTP sent"; then
    echo "   OTP request: OK"
else
    echo "   OTP request: FAILED ($OTP_RESP)"
fi

TOKEN_RESP=$(curl -sf -X POST http://localhost:8000/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone":"+919900000002","otp":"123456"}' 2>/dev/null)
if echo "$TOKEN_RESP" | grep -q "access_token"; then
    echo "   OTP verify:  OK"
    TOKEN=$(echo "$TOKEN_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
else
    echo "   OTP verify:  FAILED ($TOKEN_RESP)"
    TOKEN=""
fi

# 7. Quick animal list check
echo ""
echo "7. Animal list..."
if [ -n "$TOKEN" ]; then
    ANIMALS=$(curl -sf http://localhost:8000/v1/animals \
      -H "Authorization: Bearer $TOKEN" 2>/dev/null)
    ANIMAL_COUNT=$(echo "$ANIMALS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
    echo "   Farmer's animals: $ANIMAL_COUNT"
else
    echo "   SKIPPED (no token)"
fi

# 8. Run full scenario tests
echo ""
echo "8. Demo scenario tests..."
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR/packages/api"
if command -v uv &> /dev/null; then
    uv run python tests/test_demo_scenarios.py 2>&1 | sed 's/^/   /'
else
    python3 tests/test_demo_scenarios.py 2>&1 | sed 's/^/   /'
fi

echo ""
echo "================================="
echo "Verification complete!"
