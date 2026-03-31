## ADDED Requirements

### Requirement: Milk collection center operator interface
The milk center app SHALL provide an operator interface for receiving milk, recording quality parameters, auto-calculating rates, generating daily reports, settling farmer payments, and flagging adulteration. The interface is designed for milk collection center operators (not farmers).

#### Scenario: Receive milk from farmer
- **WHEN** the operator selects a farmer and enters milk quantity
- **THEN** the system records the collection entry with timestamp and operator ID

#### Scenario: Record quality parameters
- **WHEN** the operator enters quality readings (FAT%, SNF%, CLR, temperature)
- **THEN** the quality parameters are saved against the collection entry

#### Scenario: Auto-rate calculation from quality
- **WHEN** quality parameters are recorded for a collection entry
- **THEN** the rate per liter is auto-calculated using the FAT/SNF slab table (Karnataka Milk Federation rates) and the total amount is displayed

#### Scenario: Daily shift report
- **WHEN** the daily shift ends
- **THEN** the operator can generate a shift summary showing total collection volume, average quality (FAT%, SNF%), and farmer-wise breakdown

#### Scenario: Daily collection overview
- **WHEN** the operator opens the dashboard
- **THEN** today's total collection, number of farmers served, and average quality metrics are displayed

#### Scenario: Payment settlement generation
- **WHEN** the settlement period closes (e.g., weekly or fortnightly)
- **THEN** the system calculates farmer payments based on quantity, quality rates, and quality bonuses, and generates payment slips

#### Scenario: Quality bonus in settlement
- **WHEN** a farmer's average FAT% or SNF% exceeds the bonus threshold for the period
- **THEN** the quality bonus amount is added to the farmer's payment slip

#### Scenario: Adulteration test recording
- **WHEN** the operator records an adulteration test result (water, urea, detergent flags)
- **THEN** the flags are saved against the collection entry

#### Scenario: Adulteration alert to admin
- **WHEN** adulteration is detected in a sample
- **THEN** the collection record is flagged and an alert is sent to the admin dashboard

#### Scenario: Farmer search for milk reception
- **WHEN** the operator begins the receive milk flow
- **THEN** a searchable farmer list is displayed with recent collection history for quick selection
