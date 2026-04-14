# Production Authentication Design — PashuRaksha ERP

**Date:** 2026-04-09
**Status:** Approved
**Scope:** End-to-end OTP authentication across API, Admin, and Mobile

---

## Decisions

| Decision | Choice |
|----------|--------|
| OTP provider | Sarvam AI SMS (prod) + console log (dev) |
| Admin login UX | Phone + OTP with "Remember this device" checkbox |
| Admin role gate | Allow admin/vet/milk_center; reject farmer with friendly message |
| Token storage (web) | httpOnly cookies |
| Token storage (mobile) | expo-secure-store with Bearer header |
| CSRF protection | Double-submit cookie pattern |
| Session duration | 8 hours default, 7 days with "remember me" |
| OTP security | bcrypt-hashed in DB, 5-min expiry, 3 attempts max |
| Client detection | `client_type: "mobile"` in request body |
| Env vars | Fail fast at startup, no localhost fallbacks |
| Error responses | Structured `{ detail, code }` with machine-readable codes |

---

## 1. Authentication Flow

```
Client                    API                        OTP Provider
  |                        |                              |
  |-- POST /auth/request-otp { phone } ----------------->|
  |                        |-- (prod) Sarvam SMS -------->|
  |                        |-- (dev) log OTP to stdout    |
  |<-- 200 { message }  --|                              |
  |                        |                              |
  |-- POST /auth/verify-otp { phone, otp, remember_me?, client_type? } -->|
  |                        |-- validate OTP (hash, expiry, attempts)       |
  |                        |-- find/create User                            |
  |                        |-- check role (web clients only)               |
  |<-- Set-Cookie: token (httpOnly) -- OR -- body: { access_token } ------|
  |<-- Set-Cookie: csrf_token (JS-readable)                               |
  |<-- 200 { user_id, role, name }                                        |
```

### Rules

- OTP delivery: Sarvam AI SMS in production, console log in development. Same code path, provider selected by `settings.environment`.
- Web clients: JWT in httpOnly cookie (Secure, SameSite=Lax, Path=/). CSRF token in separate JS-readable cookie. No token in response body.
- Mobile clients: JWT in response body (`TokenResponse` schema). Stored in `expo-secure-store`. Sent as `Authorization: Bearer` header.
- Expiry: 8 hours default. 7 days when `remember_me=true`.
- Role gate (admin web only): `farmer` role rejected with friendly message. `admin`, `vet`, `milk_center` allowed.

---

## 2. API Backend

### OTP Provider Abstraction

```
app/services/otp/
  ├── __init__.py    # get_otp_provider() factory
  ├── base.py        # Abstract OTPProvider with send_otp(phone, otp) method
  ├── sarvam.py      # Production: Sarvam AI SMS API
  └── console.py     # Development: prints OTP to stdout with clear formatting
```

Provider selected by `settings.environment`. No `if __DEV__` scattered through code.

### OTP Storage and Validation

- Store OTP in `otp_requests` table: `phone`, `otp_hash` (bcrypt), `expires_at` (5 min), `attempts` (max 3)
- `UNIQUE (phone)` constraint — one active OTP per phone
- On `/request-otp`: delete existing OTP for phone, generate new 6-digit, hash with bcrypt, store, deliver via provider
- On `/verify-otp`: lookup by phone, check expiry, compare bcrypt hash, increment attempts on failure, delete row on success
- Rate limit: 5 OTP requests per phone per hour (DB-backed, not in-memory)

### Cookie-Based Auth Response (Web)

- `/verify-otp` sets two cookies:
  - `token`: httpOnly, Secure (except dev), SameSite=Lax, max-age=28800 (8h) or 604800 (7d)
  - `csrf_token`: NOT httpOnly, Secure (except dev), SameSite=Lax, same max-age
- Response body: `{ user_id, role, name }` — no token in body
- New endpoint `/auth/me`: returns current user from cookie token. Used on page reload.
- New endpoint `/auth/logout`: clears both cookies

### CSRF Middleware

- On POST/PUT/DELETE/PATCH: compare `X-CSRF-Token` header against `csrf_token` cookie value
- Skip for `/auth/request-otp` and `/auth/verify-otp` (pre-auth endpoints)
- Skip when `Authorization: Bearer` header is present (mobile clients don't use cookies)

### Rate Limiting

- Move from in-memory dict to PostgreSQL-backed (reuse existing DB)
- 5 OTP requests per phone per hour
- 3 verification attempts per OTP
- IP-based rate limit on endpoint level (existing, migrated to DB)

---

## 3. Database Schema

### New Table: `otp_requests`

```sql
CREATE TABLE otp_requests (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone       VARCHAR(15) NOT NULL,
    otp_hash    VARCHAR(128) NOT NULL,
    attempts    INTEGER NOT NULL DEFAULT 0,
    expires_at  TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_otp_phone UNIQUE (phone)
);

CREATE INDEX idx_otp_expires ON otp_requests (expires_at);
```

- No foreign key to `users` — OTP can be requested before user exists (first-time registration)
- Cleanup: delete expired rows inline (before inserting new). No separate cron needed at current scale.

### Existing `users` Table

No changes needed. Phone-based lookup, role enum, UUID primary key are all in place.

---

## 4. Admin Login Page

### File: `src/app/login/page.tsx`

Two-step MUI form:

**Step 1 — Phone entry:**
- Centered card with PashuRaksha branding
- `+91` prefix (non-editable) + phone input (10 digits, `^[6-9]\d{9}$` validation)
- "Send OTP" button, disabled until valid number
- Error states: invalid number, rate limited, network failure

**Step 2 — OTP verification:**
- Phone shown read-only with "Change" link
- 6 individual digit boxes with auto-advance and paste support
- "Remember this device" checkbox (unchecked by default)
- "Verify & Login" button, disabled until 6 digits entered
- Resend OTP link with 60-second cooldown
- Error states: wrong OTP, expired, max attempts, role not authorized

**Role gate UX:**
- `farmer` role: "This portal is for staff. Please use the PashuRaksha mobile app." No cookies set.
- `admin`/`vet`/`milk_center`: cookies set by API, redirect to `/`

### Auth Provider Changes

- Remove `crypto.randomUUID()` fallback
- Remove localStorage token storage — httpOnly cookie sent automatically
- `check()` calls `GET /auth/me` instead of checking localStorage
- `logout()` calls `POST /auth/logout` to clear cookies
- `getIdentity()` caches `/auth/me` response in memory for the session
- All `fetch` calls include `credentials: "include"`
- POST/PUT/DELETE include `X-CSRF-Token` header from csrf cookie

### Data Provider Changes

- All `fetch` calls include `credentials: "include"`
- Mutating requests include `X-CSRF-Token` header
- Remove `Authorization` header logic (cookies handle auth)

---

## 5. Mobile App Changes

### Login Screen

- Remove `__DEV__` block entirely — no mock OTP bypass
- Remove hardcoded `'mock-jwt-token'`
- Both dev and prod call same `/auth/request-otp` and `/auth/verify-otp`
- Send `client_type: "mobile"` in verify-otp request
- Store real JWT from response body in `expo-secure-store`
- Show error messages from API in Snackbar (wrong OTP, expired, rate limited)
- Add "Resend OTP" with 60-second cooldown

### API Client

- Remove localhost fallback — fail if `EXPO_PUBLIC_API_URL` not set
- On app launch: read token from SecureStore, call `/auth/me` to validate
- If expired/invalid: clear SecureStore, redirect to login

---

## 6. Security Hardening

### Environment Variable Validation (Startup)

- **API:** Fail if `DATABASE_URL`, `JWT_SECRET` missing. Fail if `SARVAM_API_KEY` missing when `environment != "development"`.
- **API:** Fail if `JWT_SECRET` < 64 hex characters (256 bits).
- **Admin:** Fail if `NEXT_PUBLIC_API_URL` not set.
- **Mobile:** Fail if `EXPO_PUBLIC_API_URL` not set.

### Cookie Flags

| Cookie | httpOnly | Secure | SameSite | Path |
|--------|----------|--------|----------|------|
| `token` | Yes | Yes (No in dev) | Lax | / |
| `csrf_token` | No | Yes (No in dev) | Lax | / |

### CORS

- Read origins from `settings.cors_origins` env var (comma-separated)
- Allow credentials (required for cookies)
- Fail at startup if empty in production

### Error Response Codes

All auth errors return `{ "detail": "message", "code": "MACHINE_CODE" }`:

| Code | Meaning |
|------|---------|
| `OTP_EXPIRED` | OTP older than 5 minutes |
| `OTP_INVALID` | Wrong OTP value |
| `OTP_MAX_ATTEMPTS` | 3 wrong attempts, OTP invalidated |
| `RATE_LIMITED` | Too many requests |
| `ROLE_NOT_AUTHORIZED` | Farmer trying to access admin |
| `TOKEN_EXPIRED` | JWT past expiry |
| `TOKEN_INVALID` | Malformed or tampered JWT |

---

## 7. Files to Create

| File | Purpose |
|------|---------|
| `api/app/services/otp/__init__.py` | Provider factory |
| `api/app/services/otp/base.py` | Abstract OTP provider |
| `api/app/services/otp/sarvam.py` | Sarvam AI SMS integration |
| `api/app/services/otp/console.py` | Dev console OTP logger |
| `api/app/models/otp.py` | OTPRequest SQLAlchemy model |
| `api/app/middleware/csrf.py` | Double-submit CSRF middleware |
| `api/alembic/versions/xxx_add_otp_requests.py` | Migration |
| `admin/src/app/login/page.tsx` | Admin login page |

## 8. Files to Modify

| File | Changes |
|------|---------|
| `api/app/routers/auth.py` | Rewrite: real OTP flow, cookie response, /me, /logout |
| `api/app/config.py` | Add startup validations, JWT secret length check |
| `api/app/main.py` | CORS from env, CSRF middleware, startup validation |
| `api/app/schemas/auth.py` | Add remember_me, client_type fields; auth error codes |
| `admin/src/providers/auth-provider.ts` | Cookie-based auth, /me endpoint, remove localStorage |
| `admin/src/providers/data-provider.ts` | credentials: include, CSRF header |
| `mobile/app/(auth)/login.tsx` | Remove mocks, real API calls, error handling |
| `mobile/src/config/api.ts` | Remove localhost fallback, fail fast |
| `mobile/src/services/voice.ts` | Remove __DEV__ mock guard |
