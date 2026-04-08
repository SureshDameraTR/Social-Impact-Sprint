#!/bin/bash
# Pre-demo warm-up script — run 5 minutes before demo
set -euo pipefail

echo "=== PashuRaksha Demo Warm-Up ==="
echo ""

echo "1. Checking Docker..."
docker compose ps
echo ""

echo "2. Checking API..."
curl -sf http://localhost:8000/health | python3 -m json.tool
echo ""

echo "3. Checking auth..."
TOKEN=$(curl -sf -X POST http://localhost:8000/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone":"+919900000002","otp":"123456"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "Token: ${TOKEN:0:20}..."
echo ""

echo "4. Checking animals..."
curl -sf http://localhost:8000/v1/animals \
  -H "Authorization: Bearer $TOKEN" | python3 -c "import sys,json; data=json.load(sys.stdin); print(f'Animals: {len(data)} found')"
echo ""

echo "5. Checking admin stats..."
ADMIN_TOKEN=$(curl -sf -X POST http://localhost:8000/v1/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phone":"+919900000001","otp":"123456"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
curl -sf http://localhost:8000/v1/admin/stats \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python3 -m json.tool
echo ""

echo "=== All checks passed — ready for demo! ==="
