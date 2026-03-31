## ADDED Requirements

### Requirement: Guided farmer onboarding flow
The mobile app SHALL provide a guided onboarding flow on first login. The flow SHALL include language selection, progressive profile building, first animal registration, a tutorial overlay, and accessibility settings. The onboarding flow SHALL appear before the home screen on first login.

#### Scenario: Welcome screen with language picker
- **WHEN** the farmer opens the app for the first time
- **THEN** a welcome screen is displayed with a language picker defaulting to Kannada (kn)

#### Scenario: Language selection applies immediately
- **WHEN** the farmer selects a language from the picker
- **THEN** all UI strings update immediately to the selected language

#### Scenario: Progressive profile builder
- **WHEN** the farmer proceeds past the welcome screen
- **THEN** a step-by-step profile form collects: name, phone (pre-filled from OTP login), district, and village

#### Scenario: First animal registration prompt
- **WHEN** the profile is completed
- **THEN** the farmer is prompted to register their first animal with a guided species icon picker and breed selector

#### Scenario: First animal added celebration
- **WHEN** the farmer successfully adds their first animal
- **THEN** the app navigates to the home screen with a congratulation card highlighting the newly added animal

#### Scenario: Tutorial overlay on first home visit
- **WHEN** the farmer reaches the home screen for the first time
- **THEN** a tutorial overlay displays 3 swipe cards explaining: voice input, health check, and sell products

#### Scenario: Accessibility toggle during onboarding
- **WHEN** the farmer is on the welcome or profile screen
- **THEN** an accessibility toggle is available for: large text, high contrast, and voice-first mode

#### Scenario: Onboarding gates home screen
- **WHEN** the farmer has not completed onboarding
- **THEN** the app redirects to the onboarding flow instead of the home screen
