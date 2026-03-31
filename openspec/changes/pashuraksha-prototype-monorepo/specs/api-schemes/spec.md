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

### Requirement: Eligibility auto-matching on profile update
The API SHALL re-evaluate scheme eligibility whenever a farmer's profile is updated (e.g., new animal added, district changed, SHG membership changed). Newly matched schemes SHALL be flagged for the farmer.

#### Scenario: Farmer adds a goat and becomes eligible for new schemes
- **WHEN** a farmer who previously only owned cattle adds a goat to their profile
- **THEN** the eligibility engine re-runs and `GET /v1/schemes/eligible?farmer_id={id}` now includes goat-specific schemes (e.g., NLM goat rearing subsidy)

#### Scenario: SHG membership unlocks NABARD schemes
- **WHEN** a farmer joins an SHG group
- **THEN** NABARD_SHG credit linkage schemes appear in their eligible schemes list

### Requirement: Application status tracking with full lifecycle
The API SHALL track scheme applications through the complete lifecycle: `submitted → under_review → approved → disbursed` (or `rejected` at any stage). Each status change SHALL record a timestamp and optional admin remarks.

#### Scenario: Application moves through full lifecycle
- **WHEN** an application progresses from submitted to disbursed
- **THEN** `GET /v1/schemes/applications/{id}` returns `{status, status_history: [{status, changed_at, changed_by, remarks}], submitted_at, approved_at, disbursed_at, disbursed_amount}`

#### Scenario: Rejected application includes reason
- **WHEN** an admin rejects an application with `{status: "rejected", remarks: "Incomplete land documents"}`
- **THEN** the application status history records the rejection reason and the farmer sees it

### Requirement: Document checklist per scheme
The API SHALL maintain a per-scheme required document list and track document upload completion for each application.

#### Scenario: Farmer views required documents for a scheme
- **WHEN** `GET /v1/schemes/{scheme_id}/documents` is called
- **THEN** the API returns `{required_documents: [{doc_type: "aadhaar_card", label: "Aadhaar Card", is_mandatory: true}, {doc_type: "land_record", label: "Land Record (RTC)", is_mandatory: true}, ...]}`

#### Scenario: Farmer uploads a document for their application
- **WHEN** `POST /v1/schemes/applications/{id}/documents` is called with `{doc_type: "aadhaar_card", file_url: "..."}`
- **THEN** the document is linked to the application and `GET /v1/schemes/applications/{id}/checklist` shows completion percentage

### Requirement: NABARD SHG credit linkage eligibility
The API SHALL check SHG membership and group grading when evaluating NABARD scheme eligibility. Only farmers in grade A or B SHG groups SHALL be eligible for NABARD credit linkage schemes.

#### Scenario: Farmer in grade-A SHG is eligible for NABARD credit
- **WHEN** `GET /v1/schemes/eligible?farmer_id={id}` is called for a farmer in a grade-A SHG
- **THEN** NABARD SHG credit linkage scheme appears with `{eligible: true, shg_grade: "A", shg_group_name: "..."}`

#### Scenario: Farmer in grade-C SHG is not eligible
- **WHEN** `GET /v1/schemes/eligible?farmer_id={id}` is called for a farmer in a grade-C SHG
- **THEN** NABARD SHG credit linkage scheme appears with `{eligible: false, reason: "SHG grading below B — current grade: C"}`
