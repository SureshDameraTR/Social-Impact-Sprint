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
