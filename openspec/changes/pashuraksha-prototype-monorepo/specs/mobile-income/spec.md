## ADDED Requirements

### Requirement: Income tab in mobile app
The farmer mobile app SHALL include an Income tab showing earnings breakdown and financial tools.

#### Scenario: Farmer views weekly earnings
- **GIVEN** an authenticated farmer with sell records
- **WHEN** they tap the Income (ಆದಾಯ) tab
- **THEN** they see a hero card with total weekly earnings (e.g., "₹2,450 ಈ ವಾರ"), comparison with last week (+12% ↑), and period selector (week/month/year)

#### Scenario: Farmer views product breakdown
- **WHEN** the farmer scrolls below the earnings hero card
- **THEN** they see a donut chart showing income by category: Milk (65%), Eggs (20%), Manure (10%), Other (5%)

#### Scenario: Farmer downloads income record
- **WHEN** the farmer taps "Download Record" (ದಾಖಲೆ ಡೌನ್‌ಲೋಡ್)
- **THEN** the app generates/downloads a PDF income statement (placeholder in prototype — shows success message)

#### Scenario: Farmer explores loan options
- **WHEN** the farmer taps the "Apply for Loan" (ಸಾಲಕ್ಕೆ ಅರ್ಜಿ) card
- **THEN** they see SHG/NABARD micro-loan information with their income data pre-filled as collateral documentation
