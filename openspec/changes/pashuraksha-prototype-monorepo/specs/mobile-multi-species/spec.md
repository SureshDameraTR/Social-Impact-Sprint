## ADDED Requirements

### Requirement: Multi-species animal management
The mobile app SHALL support cattle, goats, sheep, and poultry with species-specific icons and data fields.

#### Scenario: Farmer adds a goat
- **GIVEN** an authenticated farmer on the Add Animal screen
- **WHEN** they select the Goat (ಆಡು) icon from the species picker
- **THEN** the form adapts to show goat-relevant fields (breed options: Osmanabadi, Black Bengal, Jamunapari, Malabari) and hides cattle-specific fields (lactation_number)

#### Scenario: Home screen shows multi-species animals
- **GIVEN** a farmer with cattle, goats, and poultry registered
- **WHEN** they view the Home tab
- **THEN** each animal card shows a species-specific icon (cow 🐄, goat 🐐, sheep 🐑, chicken 🐔), and a species filter chip bar allows filtering by type

#### Scenario: Species-specific health rules
- **GIVEN** a farmer logging a health event for a goat
- **WHEN** they select symptoms on the Health screen
- **THEN** the disease triage engine uses goat-specific rules (PPR, enterotoxemia, haemonchosis) instead of cattle rules

#### Scenario: Multi-species seed data
- **GIVEN** the seed script runs
- **THEN** demo data includes: 4 cattle (existing), 2 goats, 1 sheep, 5 poultry across the 3 farmer profiles
