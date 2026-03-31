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

### Requirement: Panchsutra compliance scoring details
The API SHALL rate SHG adherence to each of the 5 NABARD Panchsutra principles individually: regular meetings, regular savings, regular internal lending, up-to-date record keeping, and timely repayment. Each criterion SHALL be scored 0.0 to 1.0 based on activity records.

#### Scenario: Group with irregular meetings scores low on that criterion
- **WHEN** an SHG group held 6 out of 12 expected monthly meetings
- **THEN** `GET /v1/shg/{group_id}/compliance` returns `panchsutra_scores.meetings: 0.5`

#### Scenario: Group with complete records scores high on books
- **WHEN** an SHG group has uploaded all monthly financial records
- **THEN** `GET /v1/shg/{group_id}/compliance` returns `panchsutra_scores.books: 1.0`

### Requirement: SHG livestock integration
The API SHALL aggregate member animal counts, total milk production, and income data across all SHG members for group-level reporting.

#### Scenario: SHG group livestock summary
- **WHEN** `GET /v1/shg/{group_id}/livestock-summary` is called
- **THEN** the API returns `{total_members, total_animals, animals_by_species: {cattle: int, goat: int, sheep: int, poultry: int}, total_milk_liters_30d, total_income_30d, avg_income_per_member}`

#### Scenario: SHG group member livestock details
- **WHEN** `GET /v1/shg/{group_id}/members/livestock` is called
- **THEN** the API returns per-member breakdown: `[{farmer_id, farmer_name, animal_count, milk_liters_30d, income_30d}]`

### Requirement: NABARD grading alignment
The API SHALL map Panchsutra compliance scores to NABARD's official A/B/C grading system. Grade A: average score >= 0.8, Grade B: average score >= 0.5, Grade C: average score < 0.5.

#### Scenario: Moderate compliance group gets grade B
- **WHEN** the average of all 5 Panchsutra scores is 0.65
- **THEN** the grading is "B"

#### Scenario: Low compliance group gets grade C
- **WHEN** the average of all 5 Panchsutra scores is 0.35
- **THEN** the grading is "C"

### Requirement: Women SHG flag
The API SHALL support marking SHG groups as women-only (`is_women_shg: true`) for gender-specific government scheme targeting. Women SHG groups SHALL be prioritized for certain NABARD and state-level schemes.

#### Scenario: Admin creates a women-only SHG
- **WHEN** `POST /v1/shg/groups` is called with `{..., is_women_shg: true}`
- **THEN** the group is created with `is_women_shg: true` and members of this group are auto-eligible for women-specific schemes

#### Scenario: Filter SHG groups by women-only flag
- **WHEN** `GET /v1/shg/groups?is_women_shg=true` is called
- **THEN** only women-only SHG groups are returned
