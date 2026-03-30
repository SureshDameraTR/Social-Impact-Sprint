## ADDED Requirements

### Requirement: Government scheme catalog
The API SHALL serve a catalog of government schemes with eligibility criteria, subsidy amounts, required documents, and active status. Schemes SHALL be pre-seeded from RGM, NLM, PKCC, LIS, and NABARD_SHG programs.

#### Scenario: Farmer views available schemes
- **WHEN** `GET /v1/schemes?is_active=true` is called
- **THEN** the API returns all active government schemes with name, description, eligibility, and subsidy details

### Requirement: Eligibility matching
The API SHALL auto-match eligible schemes for a farmer based on their profile (species owned, district, SHG membership).

#### Scenario: Farmer with cattle gets matched to RGM scheme
- **WHEN** `GET /v1/schemes/eligible?farmer_id=1` is called for a farmer who owns cattle
- **THEN** Rashtriya Gokul Mission (RGM) appears in the matched schemes list

### Requirement: Scheme application tracking
The API SHALL allow farmers to submit scheme applications and track their status through the lifecycle: draft → submitted → under_review → approved/rejected → disbursed.

#### Scenario: Farmer submits scheme application
- **WHEN** `POST /v1/schemes/apply` is called with `{scheme_id, farmer_id}`
- **THEN** the API returns `201` with `application_id` and `status: "submitted"`

#### Scenario: Admin updates application status
- **WHEN** `PUT /v1/schemes/applications/{id}/status` is called with `{status: "approved", approved_amount: 25000}`
- **THEN** the application status is updated and the farmer can see the updated status
