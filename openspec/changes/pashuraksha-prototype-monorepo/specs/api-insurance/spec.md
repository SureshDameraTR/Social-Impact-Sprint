## ADDED Requirements

### Requirement: Livestock insurance management API
The API SHALL support policy tracking, premium estimation based on risk factors, and claim filing with photo documentation for livestock insurance.

#### Scenario: Estimating insurance premium
- **WHEN** `POST /v1/insurance/estimate` is called with `{"species": "cattle", "breed": "Gir", "age_years": 4, "district_code": "RJ14", "sum_insured": 50000}`
- **THEN** the API returns `200` with `annual_premium_inr`, `subsidy_pct` (government subsidy), `farmer_share_inr`, and `risk_factors` breakdown

#### Scenario: Filing an insurance claim
- **WHEN** `POST /v1/insurance/claims` is called with `{"policy_id": "POL-2026-001", "claim_type": "death", "description": "Animal died due to illness", "photo_urls": ["url1", "url2"], "veterinary_certificate_url": "url3"}`
- **THEN** the API returns `201` with `claim_id`, `status: "pending_verification"`, and `estimated_processing_days`

#### Scenario: Querying farmer's policies
- **WHEN** `GET /v1/insurance/policies?farmer_id=42` is called
- **THEN** the API returns all active and expired policies with `policy_id`, `animal_id`, `sum_insured`, `premium_paid`, `status`, `valid_until`, and `next_premium_date`

#### Scenario: Policy renewal reminder
- **WHEN** a policy's `valid_until` date is within 30 days
- **THEN** the policy appears in queries with `renewal_alert: true` and `days_until_expiry`

### Requirement: Government subsidy integration
The API SHALL calculate applicable government subsidies (DEDS, state schemes) for livestock insurance premiums.

#### Scenario: Subsidy calculation for BPL farmer
- **WHEN** the farmer is classified as BPL AND the animal is insured under a government scheme
- **THEN** the premium estimate includes `subsidy_pct: 80` with `scheme_name` and `scheme_code`
