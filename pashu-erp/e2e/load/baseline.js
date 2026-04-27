/**
 * k6 load test baseline for PashuRaksha API.
 *
 * Run:   k6 run e2e/load/baseline.js
 * Env:   API_URL (default http://localhost:8000)
 *
 * Scenarios:
 *   baseline  — 10 VUs for 30s (steady-state)
 *   stress    — ramp to 50 VUs over 60s
 *   spike     — 100 VUs for 10s burst
 */
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const API = __ENV.API_URL || 'http://localhost:8000';
const errorRate = new Rate('errors');
const latency = new Trend('api_latency', true);

export const options = {
  scenarios: {
    baseline: {
      executor: 'constant-vus',
      vus: 10,
      duration: '30s',
      tags: { scenario: 'baseline' },
    },
    stress: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '20s', target: 25 },
        { duration: '20s', target: 50 },
        { duration: '20s', target: 0 },
      ],
      startTime: '35s',
      tags: { scenario: 'stress' },
    },
    spike: {
      executor: 'constant-vus',
      vus: 100,
      duration: '10s',
      startTime: '100s',
      tags: { scenario: 'spike' },
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<200', 'p(99)<500'],
    errors: ['rate<0.01'],
    http_req_failed: ['rate<0.01'],
  },
};

// ── Setup (runs once) ────────────────────────────────────────────────────────
// Pass token via:  k6 run -e TOKEN=<jwt> e2e/load/baseline.js
// Generate token:  python -c "from e2e.comprehensive.api_perf_phase3 import get_token, reset_otp_limits; reset_otp_limits(); print(get_token('+919900000001'))"

export function setup() {
  const token = __ENV.TOKEN;
  if (!token) {
    throw new Error('TOKEN env var required. Pre-obtain via OTP flow and pass with: k6 run -e TOKEN=<jwt> ...');
  }
  return { token };
}

// ── Main test function ───────────────────────────────────────────────────────

export default function (data) {
  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${data.token}`,
  };

  // GET /v1/admin/stats — dashboard stats
  const statsRes = http.get(`${API}/v1/admin/stats`, { headers });
  check(statsRes, { 'stats 200': (r) => r.status === 200 });
  errorRate.add(statsRes.status !== 200);
  latency.add(statsRes.timings.duration);

  // GET /v1/animals — animal list
  const animalsRes = http.get(`${API}/v1/animals?page=1&page_size=10`, { headers });
  check(animalsRes, { 'animals 200': (r) => r.status === 200 });
  errorRate.add(animalsRes.status !== 200);
  latency.add(animalsRes.timings.duration);

  // GET /v1/health — health events
  const healthRes = http.get(`${API}/v1/health`, { headers });
  check(healthRes, { 'health 200': (r) => r.status === 200 });
  errorRate.add(healthRes.status !== 200);
  latency.add(healthRes.timings.duration);

  // GET /v1/milk — milk records
  const milkRes = http.get(`${API}/v1/milk`, { headers });
  check(milkRes, { 'milk 200': (r) => r.status === 200 });
  errorRate.add(milkRes.status !== 200);
  latency.add(milkRes.timings.duration);

  // GET /v1/schemes — government schemes
  const schemesRes = http.get(`${API}/v1/schemes`, { headers });
  check(schemesRes, { 'schemes 200': (r) => r.status === 200 });
  errorRate.add(schemesRes.status !== 200);
  latency.add(schemesRes.timings.duration);

  sleep(1);
}

// ── Teardown ─────────────────────────────────────────────────────────────────

export function teardown() {
  // No cleanup needed — read-only test
}
