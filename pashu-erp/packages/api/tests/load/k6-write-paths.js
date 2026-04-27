// k6 load test for PashuRaksha ERP write paths
// Run: k6 run tests/load/k6-write-paths.js
//
// Override defaults with environment variables:
//   k6 run -e BASE_URL=http://api.example.com -e TEST_OTP=654321 tests/load/k6-write-paths.js

import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

import {
  BASE_URL,
  AUTH_PHONE,
  TEST_OTP,
  CLIENT_TYPE,
  authHeaders,
  jsonHeaders,
  randomAnimalPayload,
  randomYieldPayload,
  randomHealthPayload,
  randomSellPayload,
  duplicateAnimalPayload,
} from './k6-config.js';

// ---------------------------------------------------------------------------
// Custom metrics
// ---------------------------------------------------------------------------

const animalCreatedRate  = new Rate('animal_created_success');
const yieldRecordedRate  = new Rate('yield_recorded_success');
const healthLoggedRate   = new Rate('health_logged_success');
const saleRecordedRate   = new Rate('sale_recorded_success');
const authSuccessRate    = new Rate('auth_success');

const animalDuration = new Trend('animal_create_duration', true);
const yieldDuration  = new Trend('yield_record_duration', true);
const healthDuration = new Trend('health_log_duration', true);
const saleDuration   = new Trend('sale_record_duration', true);

// ---------------------------------------------------------------------------
// k6 options: scenarios + thresholds
// ---------------------------------------------------------------------------

export const options = {
  scenarios: {
    // Scenario 1: milk yield recording (heaviest expected traffic)
    milk_recording: {
      executor:   'constant-vus',
      vus:        parseInt(__ENV.MILK_VUS || '20', 10),
      duration:   __ENV.DURATION || '2m',
      exec:       'milkRecording',
      tags:       { scenario: 'milk_recording' },
      startTime:  '0s',
    },

    // Scenario 2: animal registration (lower volume)
    animal_registration: {
      executor:   'constant-vus',
      vus:        parseInt(__ENV.ANIMAL_VUS || '5', 10),
      duration:   __ENV.DURATION || '2m',
      exec:       'animalRegistration',
      tags:       { scenario: 'animal_registration' },
      startTime:  '0s',
    },

    // Scenario 3: health event logging (moderate volume)
    health_events: {
      executor:   'constant-vus',
      vus:        parseInt(__ENV.HEALTH_VUS || '10', 10),
      duration:   __ENV.DURATION || '2m',
      exec:       'healthEvents',
      tags:       { scenario: 'health_events' },
      startTime:  '0s',
    },

    // Scenario 4: mixed writes (realistic traffic pattern)
    mixed_writes: {
      executor:   'constant-vus',
      vus:        parseInt(__ENV.MIXED_VUS || '10', 10),
      duration:   __ENV.DURATION || '2m',
      exec:       'mixedWrites',
      tags:       { scenario: 'mixed_writes' },
      startTime:  '0s',
    },
  },

  thresholds: {
    // Per-scenario latency
    'http_req_duration{scenario:milk_recording}':       ['p(95)<500'],
    'http_req_duration{scenario:animal_registration}':  ['p(95)<500'],
    'http_req_duration{scenario:health_events}':        ['p(95)<500'],
    'http_req_duration{scenario:mixed_writes}':         ['p(95)<500'],

    // Global error rate: less than 1% failures
    'http_req_failed': ['rate<0.01'],

    // Minimum aggregate throughput: at least 50 req/s
    'http_reqs': ['rate>50'],

    // Custom success rates (informational, not gating)
    'animal_created_success': ['rate>0.95'],
    'yield_recorded_success': ['rate>0.95'],
    'health_logged_success':  ['rate>0.95'],
    'sale_recorded_success':  ['rate>0.95'],
  },
};

// ---------------------------------------------------------------------------
// Setup: authenticate and obtain a bearer token + seed an animal
// ---------------------------------------------------------------------------

export function setup() {
  console.log(`Authenticating against ${BASE_URL} with phone ${AUTH_PHONE}`);

  // Step 1: Request OTP
  const otpReqRes = http.post(
    `${BASE_URL}/v1/auth/request-otp`,
    JSON.stringify({ phone: AUTH_PHONE }),
    { headers: jsonHeaders(), tags: { name: 'auth_request_otp' } },
  );

  const otpRequested = check(otpReqRes, {
    'OTP request status is 200': (r) => r.status === 200,
  });

  if (!otpRequested) {
    console.error(`OTP request failed: ${otpReqRes.status} ${otpReqRes.body}`);
    // Continue anyway -- the OTP may already be active from a prior run
  }

  // Brief pause to let the OTP get stored
  sleep(1);

  // Step 2: Verify OTP and get token
  const verifyRes = http.post(
    `${BASE_URL}/v1/auth/verify-otp`,
    JSON.stringify({
      phone:       AUTH_PHONE,
      otp:         TEST_OTP,
      client_type: CLIENT_TYPE,
    }),
    { headers: jsonHeaders(), tags: { name: 'auth_verify_otp' } },
  );

  const verified = check(verifyRes, {
    'OTP verify status is 200': (r) => r.status === 200,
    'Response contains access_token': (r) => {
      try { return JSON.parse(r.body).access_token !== undefined; }
      catch { return false; }
    },
  });

  if (!verified) {
    console.error(`OTP verify failed: ${verifyRes.status} ${verifyRes.body}`);
    throw new Error('Setup failed: could not authenticate. Is the API running? Is the test OTP correct?');
  }

  const authData = JSON.parse(verifyRes.body);
  const token    = authData.access_token;
  const userId   = authData.user_id;

  console.log(`Authenticated as user ${userId} (role: ${authData.role})`);

  // Step 3: Seed a test animal so milk and health scenarios have a valid animal_id
  const animalPayload = {
    name:       'LoadTestCow',
    species:    'cattle',
    breed:      'Hallikar',
    breed_type: 'indigenous',
    sex:        'female',
    lactation_number: 3,
  };

  const animalRes = http.post(
    `${BASE_URL}/v1/animals`,
    JSON.stringify(animalPayload),
    { headers: authHeaders(token), tags: { name: 'setup_create_animal' } },
  );

  let seedAnimalId = null;
  if (animalRes.status === 201) {
    seedAnimalId = JSON.parse(animalRes.body).id;
    console.log(`Seed animal created: ${seedAnimalId}`);
  } else {
    console.warn(`Could not seed animal (${animalRes.status}). Milk/health scenarios will create their own.`);
  }

  return { token, userId, seedAnimalId };
}

// ---------------------------------------------------------------------------
// Scenario executors
// ---------------------------------------------------------------------------

/**
 * Scenario: milk_recording
 * POST /v1/milk/yield with randomized quantities and sessions.
 */
export function milkRecording(data) {
  const { token, seedAnimalId } = data;

  group('milk yield recording', () => {
    let animalId = seedAnimalId;

    // If no seed animal, create one on the fly
    if (!animalId) {
      animalId = _createAnimalAndGetId(token);
      if (!animalId) {
        console.warn('Skipping milk yield -- no animal available');
        sleep(1);
        return;
      }
    }

    const payload = randomYieldPayload(animalId);
    const res = http.post(
      `${BASE_URL}/v1/milk/yield`,
      JSON.stringify(payload),
      { headers: authHeaders(token), tags: { name: 'POST /v1/milk/yield' } },
    );

    const success = check(res, {
      'milk yield status is 201': (r) => r.status === 201,
      'response has id':          (r) => {
        try { return JSON.parse(r.body).id !== undefined; }
        catch { return false; }
      },
    });

    yieldRecordedRate.add(success ? 1 : 0);
    yieldDuration.add(res.timings.duration);
  });

  sleep(1);
}

/**
 * Scenario: animal_registration
 * POST /v1/animals with randomized breeds, species, and names.
 */
export function animalRegistration(data) {
  const { token } = data;

  group('animal registration', () => {
    const payload = randomAnimalPayload();
    const res = http.post(
      `${BASE_URL}/v1/animals`,
      JSON.stringify(payload),
      { headers: authHeaders(token), tags: { name: 'POST /v1/animals' } },
    );

    const success = check(res, {
      'animal create status is 201': (r) => r.status === 201,
      'response has pashu_aadhaar_id': (r) => {
        try { return JSON.parse(r.body).pashu_aadhaar_id !== undefined; }
        catch { return false; }
      },
    });

    animalCreatedRate.add(success ? 1 : 0);
    animalDuration.add(res.timings.duration);

    // Edge case: attempt duplicate animal name (should still succeed --
    // the API auto-generates a unique pashu_aadhaar_id)
    if (Math.random() < 0.1) {
      const dupPayload = duplicateAnimalPayload();
      const dupRes = http.post(
        `${BASE_URL}/v1/animals`,
        JSON.stringify(dupPayload),
        { headers: authHeaders(token), tags: { name: 'POST /v1/animals (duplicate name)' } },
      );

      check(dupRes, {
        'duplicate name still creates (201)': (r) => r.status === 201,
      });
    }
  });

  sleep(1);
}

/**
 * Scenario: health_events
 * POST /v1/health/log with varied symptoms and event types.
 */
export function healthEvents(data) {
  const { token, seedAnimalId } = data;

  group('health event logging', () => {
    let animalId = seedAnimalId;

    if (!animalId) {
      animalId = _createAnimalAndGetId(token);
      if (!animalId) {
        console.warn('Skipping health event -- no animal available');
        sleep(1);
        return;
      }
    }

    const payload = randomHealthPayload(animalId);
    const res = http.post(
      `${BASE_URL}/v1/health/log`,
      JSON.stringify(payload),
      { headers: authHeaders(token), tags: { name: 'POST /v1/health/log' } },
    );

    const success = check(res, {
      'health log status is 201': (r) => r.status === 201,
      'response has risk_score':  (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.ai_risk_score !== undefined;
        } catch { return false; }
      },
    });

    healthLoggedRate.add(success ? 1 : 0);
    healthDuration.add(res.timings.duration);
  });

  sleep(1);
}

/**
 * Scenario: mixed_writes
 * Randomly pick between milk yield, animal registration, health event, and sale.
 */
export function mixedWrites(data) {
  const { token, seedAnimalId } = data;
  const dice = Math.random();

  if (dice < 0.35) {
    // 35% milk yield
    _doMilkYield(token, seedAnimalId);
  } else if (dice < 0.55) {
    // 20% animal registration
    _doAnimalCreate(token);
  } else if (dice < 0.80) {
    // 25% health event
    _doHealthEvent(token, seedAnimalId);
  } else {
    // 20% marketplace sale
    _doSale(token);
  }

  sleep(1);
}

// ---------------------------------------------------------------------------
// Teardown (optional cleanup reporting)
// ---------------------------------------------------------------------------

export function teardown(data) {
  console.log('Load test complete.');
  if (data && data.userId) {
    console.log(`Test user: ${data.userId}`);
  }
  console.log('Review results above. Clean up test data in the database if needed.');
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Create an animal and return its ID, or null on failure.
 */
function _createAnimalAndGetId(token) {
  const payload = randomAnimalPayload();
  // Force female cattle so milk yield makes sense
  payload.species = 'cattle';
  payload.sex = 'female';

  const res = http.post(
    `${BASE_URL}/v1/animals`,
    JSON.stringify(payload),
    { headers: authHeaders(token), tags: { name: 'POST /v1/animals (helper)' } },
  );

  if (res.status === 201) {
    try {
      return JSON.parse(res.body).id;
    } catch {
      return null;
    }
  }
  return null;
}

function _doMilkYield(token, seedAnimalId) {
  group('mixed: milk yield', () => {
    let animalId = seedAnimalId;
    if (!animalId) {
      animalId = _createAnimalAndGetId(token);
      if (!animalId) return;
    }

    const payload = randomYieldPayload(animalId);
    const res = http.post(
      `${BASE_URL}/v1/milk/yield`,
      JSON.stringify(payload),
      { headers: authHeaders(token), tags: { name: 'POST /v1/milk/yield (mixed)' } },
    );

    const ok = check(res, { 'mixed milk yield 201': (r) => r.status === 201 });
    yieldRecordedRate.add(ok ? 1 : 0);
    yieldDuration.add(res.timings.duration);
  });
}

function _doAnimalCreate(token) {
  group('mixed: animal create', () => {
    const payload = randomAnimalPayload();
    const res = http.post(
      `${BASE_URL}/v1/animals`,
      JSON.stringify(payload),
      { headers: authHeaders(token), tags: { name: 'POST /v1/animals (mixed)' } },
    );

    const ok = check(res, { 'mixed animal create 201': (r) => r.status === 201 });
    animalCreatedRate.add(ok ? 1 : 0);
    animalDuration.add(res.timings.duration);
  });
}

function _doHealthEvent(token, seedAnimalId) {
  group('mixed: health event', () => {
    let animalId = seedAnimalId;
    if (!animalId) {
      animalId = _createAnimalAndGetId(token);
      if (!animalId) return;
    }

    const payload = randomHealthPayload(animalId);
    const res = http.post(
      `${BASE_URL}/v1/health/log`,
      JSON.stringify(payload),
      { headers: authHeaders(token), tags: { name: 'POST /v1/health/log (mixed)' } },
    );

    const ok = check(res, { 'mixed health log 201': (r) => r.status === 201 });
    healthLoggedRate.add(ok ? 1 : 0);
    healthDuration.add(res.timings.duration);
  });
}

function _doSale(token) {
  group('mixed: marketplace sale', () => {
    const payload = randomSellPayload();
    const res = http.post(
      `${BASE_URL}/v1/marketplace/sell`,
      JSON.stringify(payload),
      { headers: authHeaders(token), tags: { name: 'POST /v1/marketplace/sell (mixed)' } },
    );

    const ok = check(res, { 'mixed sale 201': (r) => r.status === 201 });
    saleRecordedRate.add(ok ? 1 : 0);
    saleDuration.add(res.timings.duration);
  });
}
