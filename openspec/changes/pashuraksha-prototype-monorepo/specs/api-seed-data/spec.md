## ADDED Requirements

### Requirement: Idempotent seed script with realistic Karnataka demo data
The API SHALL include a seed script that populates the database with realistic demo data. The script SHALL be idempotent — safe to run multiple times without duplicating data.

#### Scenario: Seed script creates demo data
- **WHEN** the seed script is executed against an empty database
- **THEN** it creates: 3 farmers (with Karnataka village names and Kannada names), 1 admin user, 8 animals (mix of cattle and buffalo with breed-appropriate names), 1 milk collection center, 30 days of milk collection records with realistic yield variance, health events including at least 1 high-risk case, vaccinations, transactions, 2 SHG groups, and 5 government schemes

#### Scenario: Seed script is idempotent
- **WHEN** the seed script is executed a second time
- **THEN** no duplicate records are created (uses upsert or existence checks)

#### Scenario: Demo scenario 1 data exists
- **WHEN** the seed script completes
- **THEN** farmer "Lakshmi" (phone: 9876543210) exists with cow "Lakshmi" (Hallikar breed) with a Pashu Aadhaar ID

#### Scenario: Demo scenario 3 data exists
- **WHEN** the seed script completes
- **THEN** 30 days of milk records exist for at least 2 animals with realistic variance (3-7 liters/day for local breeds)

### Requirement: Multi-species seed data
The seed script SHALL include animals beyond cattle and buffalo: 2 goats (Osmanabadi breed), 1 sheep (Bannur breed), and 5 poultry (Giriraja breed) assigned across demo farmers.

#### Scenario: Goat seed data exists
- **WHEN** the seed script completes
- **THEN** 2 goats exist with Osmanabadi breed, assigned to farmer "Ravi", with health records and vaccination history

#### Scenario: Poultry seed data exists
- **WHEN** the seed script completes
- **THEN** 5 poultry (Giriraja) exist assigned to farmer "Meena" with egg production records

### Requirement: Weather mock data
The seed script SHALL include 7 days of weather forecast mock data for Mysore and Mandya districts with temperature, humidity, rainfall, and wind speed.

#### Scenario: Weather data exists for demo districts
- **WHEN** the seed script completes
- **THEN** 7 days of weather data exist for both Mysore and Mandya with realistic Karnataka summer values (28-38C, 40-80% humidity) and THI-based heat stress indicators

### Requirement: Feed ingredients seed data
The seed script SHALL include 30 common Karnataka feed ingredients with NDDB nutritional values (crude protein, TDN, dry matter percentage).

#### Scenario: Feed ingredients data exists
- **WHEN** the seed script completes
- **THEN** 30 feed ingredients exist including ragi straw, jowar kadbi, groundnut cake, cotton seed, maize grain, with `{name_en, name_kn, crude_protein_pct, tdn_pct, dry_matter_pct, cost_per_kg, source: "NDDB"}`

### Requirement: Traditional remedies seed data
The seed script SHALL include 25 ethno-veterinary remedies documented by ICAR for common livestock ailments.

#### Scenario: Traditional remedies data exists
- **WHEN** the seed script completes
- **THEN** 25 remedies exist with `{name_kn, name_en, ailment, ingredients, preparation, dosage, species_applicable, source: "ICAR Ethno-Vet Documentation"}` including remedies for bloat, diarrhea, mastitis, wound healing, and tick infestation

### Requirement: Insurance policies seed data
The seed script SHALL include 3 active insurance policies and 1 claim for demo scenarios.

#### Scenario: Insurance demo data exists
- **WHEN** the seed script completes
- **THEN** 3 active policies exist under PKCC (Pashu Kisan Credit Card) with `{policy_id, farmer_id, animal_id, provider: "UIIC", sum_insured, premium_paid, valid_from, valid_to, status: "active"}` and 1 claim with `{claim_id, policy_id, reason: "accidental death", claim_amount, status: "approved", disbursed_on}`

### Requirement: Community alerts seed data
The seed script SHALL include 2 disease alert records near demo farm GPS coordinates for testing the community alert feature.

#### Scenario: Community alert demo data exists
- **WHEN** the seed script completes
- **THEN** 2 community alerts exist: one for FMD near Mysore (12.30N, 76.65E, radius 10km, status: "active") and one resolved PPR alert near Mandya (12.52N, 76.90E, status: "resolved")

### Requirement: Medicine withdrawal seed data
The seed script SHALL include 15 common veterinary medicines with ICAR/FSSAI withdrawal periods for milk and meat.

#### Scenario: Medicine withdrawal data exists
- **WHEN** the seed script completes
- **THEN** 15 medicines exist with `{name, category, milk_withdrawal_days, meat_withdrawal_days, common_usage, dosage_notes, source: "ICAR/FSSAI"}` including Oxytetracycline (milk: 7d, meat: 28d), Ivermectin (milk: 5d, meat: 35d), Enrofloxacin (milk: 5d, meat: 14d)

### Requirement: Vaccination schedule seed data
The seed script SHALL include ICAR-recommended vaccination calendar entries for cattle, goat, sheep, and poultry.

#### Scenario: Vaccination schedule data exists
- **WHEN** the seed script completes
- **THEN** vaccination schedule entries exist for: cattle (HS, BQ, FMD, Brucella, Anthrax), goat (PPR, Enterotoxemia, Goat Pox), sheep (PPR, Bluetongue, Enterotoxemia, Sheep Pox), poultry (Newcastle, Marek's, IBD, Fowl Pox) with `{species, vaccine_name, first_dose_age_days, booster_interval_days, route, source: "ICAR"}`
