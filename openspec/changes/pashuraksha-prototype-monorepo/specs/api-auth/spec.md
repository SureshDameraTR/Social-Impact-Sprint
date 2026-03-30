## ADDED Requirements

### Requirement: Mock OTP login flow
The auth system SHALL accept any phone number and validate OTP "123456" (hardcoded for prototype). On successful OTP verification, the system SHALL return a JWT access token.

#### Scenario: Farmer requests OTP
- **WHEN** `POST /v1/auth/request-otp` is called with `{"phone": "9876543210"}`
- **THEN** the API returns `200 {"message": "OTP sent"}` (no actual SMS sent)

#### Scenario: Farmer verifies correct OTP
- **WHEN** `POST /v1/auth/verify-otp` is called with `{"phone": "9876543210", "otp": "123456"}`
- **THEN** the API returns `200 {"access_token": "<jwt>", "token_type": "bearer", "user": {...}}`

#### Scenario: Farmer verifies wrong OTP
- **WHEN** `POST /v1/auth/verify-otp` is called with an incorrect OTP
- **THEN** the API returns `401 {"detail": "Invalid OTP"}`

### Requirement: JWT HS256 token issuance and validation
The auth system SHALL issue JWT tokens signed with HS256 using a configurable `SECRET_KEY`. Tokens SHALL contain `user_id`, `role`, and `exp` claims. Token expiry SHALL be 24 hours (configurable).

#### Scenario: Protected endpoint rejects missing token
- **WHEN** `GET /v1/animals` is called without an Authorization header
- **THEN** the API returns `401 {"detail": "Not authenticated"}`

#### Scenario: Protected endpoint accepts valid token
- **WHEN** `GET /v1/animals` is called with `Authorization: Bearer <valid_jwt>`
- **THEN** the API returns the animals list for the authenticated user

#### Scenario: Expired token is rejected
- **WHEN** a request is made with an expired JWT token
- **THEN** the API returns `401 {"detail": "Token expired"}`

### Requirement: Auto-create user on first login
The auth system SHALL create a new user record if the phone number does not exist in the database. The default role SHALL be "farmer" and default language SHALL be "kn" (Kannada).

#### Scenario: New phone number creates user
- **WHEN** OTP is verified for a phone number not in the database
- **THEN** a new user record is created with `role="farmer"`, `lang_pref="kn"`, and the JWT is issued for this new user
