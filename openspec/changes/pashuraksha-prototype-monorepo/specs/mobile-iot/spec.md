## ADDED Requirements

### Requirement: Smart Farm / IoT mockup screen
The mobile app SHALL include a Smart Farm screen showing a preview of IoT capabilities (Phase 2 feature).

#### Scenario: Farmer accesses Smart Farm screen
- **GIVEN** an authenticated farmer on the home screen
- **WHEN** they tap the Smart Farm icon (🌐) in the header
- **THEN** they see a GPS map with mock animal location markers and a "Phase 2 — Coming Soon" banner

#### Scenario: Farmer views device status
- **WHEN** the farmer scrolls below the map on the Smart Farm screen
- **THEN** they see device status cards: RFID Scanner (Online ✓), Milk Quality Meter (Offline ✗), GPS Collar (3 active), Smart Feeder (Auto-mode)

#### Scenario: All IoT data is clearly labeled as mockup
- **GIVEN** the Smart Farm screen is displayed
- **THEN** a prominent banner states "ಭವಿಷ್ಯದ ವೈಶಿಷ್ಟ್ಯ — ಹಂತ 2" (Future Feature — Phase 2) to set correct expectations with stakeholders
