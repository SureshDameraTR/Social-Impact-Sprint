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

### Requirement: Multi-species disease rules
The triage engine SHALL include species-specific disease rule sets beyond cattle: goat (PPR, enterotoxemia, Johne's disease), sheep (bluetongue, foot rot), and poultry (Newcastle disease, Marek's disease, avian influenza). Each rule set SHALL reference ICAR-IVRI guidelines for the respective species.

#### Scenario: Goat symptoms trigger PPR assessment
- **WHEN** symptoms `fever_above_104`, `mouth_ulcers`, `diarrhea` are logged for a goat
- **THEN** the triage returns `risk_level: "high"`, `probable_diseases: ["Peste des Petits Ruminants (PPR)"]`, `action: "EMERGENCY_VET_CONSULT"`, `species_rules: "goat"`

#### Scenario: Poultry symptoms trigger Newcastle assessment
- **WHEN** symptoms `respiratory_distress`, `greenish_diarrhea`, `twisted_neck` are logged for poultry
- **THEN** the triage returns `risk_level: "high"`, `probable_diseases: ["Newcastle Disease"]`, `action: "EMERGENCY_VET_CONSULT"`, `species_rules: "poultry"`

#### Scenario: Sheep symptoms trigger bluetongue assessment
- **WHEN** symptoms `swollen_tongue`, `lameness`, `fever` are logged for a sheep
- **THEN** the triage returns `risk_level: "high"`, `probable_diseases: ["Bluetongue"]`, `action: "EMERGENCY_VET_CONSULT"`, `species_rules: "sheep"`

### Requirement: Community alert triggering
The API SHALL auto-create a community alert when a health event produces a risk score above 80. The alert SHALL notify nearby farmers (within a configurable radius, default 10km) based on GPS coordinates.

#### Scenario: High-risk event triggers community alert
- **WHEN** a health event is logged with `ai_risk_score > 80`
- **THEN** the API creates a community alert with `{alert_type: "DISEASE_WARNING", source_event_id, species, probable_diseases, affected_gps, radius_km: 10}` and returns it in the health event response as `community_alert_id`

#### Scenario: Nearby farmers can view community alerts
- **WHEN** `GET /v1/health/community-alerts?lat={lat}&lng={lng}&radius_km=10` is called
- **THEN** the API returns active alerts within the specified radius sorted by proximity

### Requirement: Outbreak report creation
The API SHALL automatically create an OUTBREAK_REPORT when 3 or more high-risk health events (risk_level: "high") are clustered within 5km and 7 days. The report SHALL aggregate affected animals, farmers, and probable diseases.

#### Scenario: Cluster of high-risk events triggers outbreak report
- **WHEN** 3 high-risk health events occur within 5km radius and 7-day window
- **THEN** the API creates `{report_type: "OUTBREAK_REPORT", affected_animal_count, affected_farmer_count, probable_diseases, centroid_gps, radius_km, status: "ACTIVE"}` and notifies admin users

#### Scenario: Admin views outbreak reports
- **WHEN** `GET /v1/health/outbreak-reports?status=ACTIVE` is called by an admin
- **THEN** the API returns active outbreak reports with containment status and affected area details

### Requirement: Medicine withdrawal tracking
The API SHALL link medicine administration records to health events and auto-calculate withdrawal periods for milk and meat. Withdrawal dates SHALL be based on ICAR/FSSAI guidelines per medicine.

#### Scenario: Farmer records medicine administration
- **WHEN** `POST /v1/health/medicines` is called with `{animal_id, health_event_id, medicine_name, dosage, administered_on}`
- **THEN** the API returns the record with `milk_withdrawal_until` and `meat_withdrawal_until` dates calculated from the medicine's withdrawal period

#### Scenario: Farmer checks withdrawal status
- **WHEN** `GET /v1/health/medicines/withdrawal-status/{animal_id}` is called
- **THEN** the API returns `{animal_id, active_withdrawals: [{medicine_name, milk_safe_from, meat_safe_from, days_remaining}], is_milk_safe: bool, is_meat_safe: bool}`
