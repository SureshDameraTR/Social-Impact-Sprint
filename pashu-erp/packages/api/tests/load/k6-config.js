// Shared configuration and helpers for PashuRaksha k6 load tests.
//
// Usage (from other k6 scripts):
//   import { BASE_URL, AUTH_PHONE, TEST_OTP, authHeaders, randomAnimalPayload } from './k6-config.js';

// ---------------------------------------------------------------------------
// Environment-configurable settings
// ---------------------------------------------------------------------------

export const BASE_URL      = __ENV.BASE_URL      || 'http://localhost:8000';
export const AUTH_PHONE    = __ENV.AUTH_PHONE     || '+919900000001';
export const TEST_OTP      = __ENV.TEST_OTP      || '123456';
export const CLIENT_TYPE   = __ENV.CLIENT_TYPE    || 'mobile';

// ---------------------------------------------------------------------------
// Auth helpers
// ---------------------------------------------------------------------------

/**
 * Build an Authorization header object from a bearer token.
 */
export function authHeaders(token) {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };
}

/**
 * Build headers for unauthenticated requests.
 */
export function jsonHeaders() {
  return { 'Content-Type': 'application/json' };
}

// ---------------------------------------------------------------------------
// Random data generators
// ---------------------------------------------------------------------------

const SPECIES  = ['cattle', 'goat', 'sheep', 'poultry'];
const BREEDS   = {
  cattle:  ['Hallikar', 'Amrit Mahal', 'Gir', 'Sahiwal', 'Red Sindhi', 'Tharparkar'],
  goat:    ['Osmanabadi', 'Jamunapari', 'Beetal', 'Sirohi', 'Barbari'],
  sheep:   ['Deccani', 'Nellore', 'Mandya', 'Hassan', 'Bannur'],
  poultry: ['Kadaknath', 'Aseel', 'Giriraja', 'Vanaraja'],
};
const BREED_TYPES = ['indigenous', 'crossbreed', 'exotic'];
const SEXES       = ['male', 'female'];
const SESSIONS    = ['morning', 'evening'];
const NAMES       = [
  'Lakshmi', 'Ganga', 'Nandini', 'Kamala', 'Bhavani',
  'Sundari', 'Parvati', 'Radha', 'Gauri', 'Janaki',
  'Raja', 'Krishna', 'Shiva', 'Ramu', 'Basava',
];

const SYMPTOMS_POOL = [
  'fever', 'lethargy', 'loss_of_appetite', 'nasal_discharge',
  'coughing', 'diarrhea', 'swollen_joints', 'lameness',
  'skin_lesions', 'excessive_salivation', 'bloating',
  'reduced_milk_yield', 'eye_discharge', 'weight_loss',
  'labored_breathing', 'dehydration',
];

const EVENT_TYPES    = ['symptom', 'checkup', 'treatment', 'emergency'];
const PRODUCT_TYPES  = ['milk', 'eggs', 'goat_products', 'sheep_products', 'manure', 'wool', 'other'];
const PRODUCT_UNITS  = { milk: 'liters', eggs: 'dozen', goat_products: 'kg', sheep_products: 'kg', manure: 'kg', wool: 'kg', other: 'units' };
const BUYER_NAMES    = ['Ramesh', 'Suresh', 'Mahesh', 'Nagaraj', 'Prakash', 'Venkatesh', 'Girish'];

function pick(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomDecimal(min, max, decimals) {
  const val = Math.random() * (max - min) + min;
  return parseFloat(val.toFixed(decimals));
}

function randomSubset(arr, minCount, maxCount) {
  const count = randomInt(minCount, Math.min(maxCount, arr.length));
  const shuffled = arr.slice().sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
}

// ---------------------------------------------------------------------------
// Payload factories
// ---------------------------------------------------------------------------

/**
 * Generate a random AnimalCreate payload.
 */
export function randomAnimalPayload() {
  const species = pick(SPECIES);
  return {
    name:        pick(NAMES),
    species:     species,
    breed:       pick(BREEDS[species]),
    breed_type:  pick(BREED_TYPES),
    sex:         pick(SEXES),
    date_of_birth: `${randomInt(2015, 2024)}-${String(randomInt(1, 12)).padStart(2, '0')}-${String(randomInt(1, 28)).padStart(2, '0')}`,
    lactation_number: species === 'cattle' ? randomInt(0, 8) : null,
    body_condition_score: randomDecimal(1.0, 5.0, 1),
    is_insured:  Math.random() > 0.7,
  };
}

/**
 * Generate a random YieldLogCreate payload.
 * Requires a valid animal_id.
 */
export function randomYieldPayload(animalId) {
  return {
    animal_id:       animalId,
    quantity_liters: randomDecimal(1.0, 15.0, 2),
    session:         pick(SESSIONS),
    notes:           Math.random() > 0.5 ? `Load test entry ${Date.now()}` : null,
  };
}

/**
 * Generate a random HealthEventCreate payload.
 * Requires a valid animal_id.
 */
export function randomHealthPayload(animalId) {
  return {
    animal_id:   animalId,
    event_type:  pick(EVENT_TYPES),
    description: `Load test health event ${Date.now()}`,
    symptoms:    randomSubset(SYMPTOMS_POOL, 1, 4),
  };
}

/**
 * Generate a random SellRecordCreate payload.
 */
export function randomSellPayload() {
  const productType = pick(PRODUCT_TYPES);
  return {
    product_type:   productType,
    quantity:        randomDecimal(1.0, 50.0, 2),
    unit:            PRODUCT_UNITS[productType] || 'units',
    price_per_unit:  randomDecimal(10.0, 200.0, 2),
    buyer_name:      pick(BUYER_NAMES),
    buyer_phone:     `+91${randomInt(6000000000, 9999999999)}`,
    notes:           Math.random() > 0.6 ? `Load test sale ${Date.now()}` : null,
  };
}

/**
 * Generate a duplicate animal payload (same name + species) for edge-case testing.
 */
export function duplicateAnimalPayload() {
  return {
    name:       'DuplicateTestAnimal',
    species:    'cattle',
    breed:      'Hallikar',
    breed_type: 'indigenous',
    sex:        'female',
  };
}
