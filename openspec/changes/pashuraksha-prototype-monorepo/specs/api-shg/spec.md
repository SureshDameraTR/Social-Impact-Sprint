## ADDED Requirements

### Requirement: SHG group management
The API SHALL provide CRUD for Self-Help Group records with NABARD-required fields including registration number, promoting institution, formation date, and bank linkage details.

#### Scenario: Admin creates an SHG group
- **WHEN** `POST /v1/shg/groups` is called with group name, district, village_code, and admin_user_id
- **THEN** the API returns `201` with the group record including auto-generated `id`

#### Scenario: List SHG groups by district
- **WHEN** `GET /v1/shg/groups?district=Mysore` is called
- **THEN** the API returns SHG groups filtered by the specified district

### Requirement: NABARD Panchsutra compliance scoring
The API SHALL compute a compliance score based on the 5 NABARD Panchsutra criteria: regular meetings, regular savings, regular internal lending, regular repayment, and up-to-date books.

#### Scenario: View compliance score for a group
- **WHEN** `GET /v1/shg/{group_id}/compliance` is called
- **THEN** the API returns `{panchsutra_scores: {meetings: float, savings: float, lending: float, repayment: float, books: float}, grading: "A"|"B"|"C"}`

#### Scenario: Group with perfect compliance gets grade A
- **WHEN** all 5 Panchsutra scores are above 0.8
- **THEN** the grading is "A"
