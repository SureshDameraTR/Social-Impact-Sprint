## ADDED Requirements

### Requirement: Health event logging with symptom tracking
The API SHALL allow farmers to log health events for their animals with event type, description, and optional symptom codes.

#### Scenario: Farmer logs a health event
- **WHEN** `POST /v1/health/log` is called with `{"animal_id": 1, "event_type": "symptom", "description": "Not eating, nasal discharge", "symptoms": ["reduced_appetite", "nasal_discharge"]}`
- **THEN** the API returns `201` with the health event including `id`, `event_date`, and `ai_risk_score` from the rule engine

#### Scenario: Farmer views health timeline
- **WHEN** `GET /v1/health/history/{animal_id}` is called
- **THEN** the API returns health events sorted by `event_date` descending with pagination

### Requirement: Rule-based disease triage engine
The API SHALL evaluate logged symptoms against 50+ veterinary rules from ICAR-IVRI/NDDB guidelines and return a risk assessment. The engine SHALL NOT use ML models.

#### Scenario: High-risk symptoms trigger emergency alert
- **WHEN** symptoms include `fever_above_104` AND `nasal_discharge`
- **THEN** the triage returns `risk_level: "high"`, `probable_diseases: ["Hemorrhagic Septicemia", "Foot-and-Mouth Disease"]`, `action: "EMERGENCY_VET_CONSULT"`, `source: "ICAR-IVRI Clinical Manual"`

#### Scenario: Low-risk symptoms return watch status
- **WHEN** symptoms include only `reduced_appetite` without other indicators
- **THEN** the triage returns `risk_level: "low"`, `action: "MONITOR_48H"`, with general care recommendations

#### Scenario: Unknown symptom combination returns moderate risk
- **WHEN** symptoms do not match any specific rule
- **THEN** the triage returns `risk_level: "moderate"`, `action: "VET_CONSULT_24H"` as a safe default

### Requirement: Vaccination tracking
The API SHALL provide CRUD for vaccination records linked to animals with `vaccine_name`, `administered_on`, `next_due`, and `batch_number`.

#### Scenario: Farmer records a vaccination
- **WHEN** `POST /v1/health/vaccinations` is called with animal_id, vaccine details, and next due date
- **THEN** the vaccination record is created and linked to the animal

#### Scenario: Farmer views upcoming vaccinations
- **WHEN** `GET /v1/health/vaccinations/{animal_id}` is called
- **THEN** the API returns completed and upcoming vaccinations sorted by date
