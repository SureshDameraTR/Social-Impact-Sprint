## ADDED Requirements

### Requirement: Insurance management screen in mobile app
The mobile app SHALL provide an insurance management screen where farmers can view policies, estimate premiums, file claims with photo evidence, and track claim status. Notifications SHALL alert farmers to status changes.

#### Scenario: Farmer views insurance policies
- **WHEN** the farmer opens the insurance screen
- **THEN** all policies are displayed grouped by active and expired, showing animal name, coverage amount, and premium due date

#### Scenario: Premium calculator
- **WHEN** the farmer taps "Estimate Premium"
- **THEN** a calculator screen accepts species, breed, age, and district to display an estimated premium amount

#### Scenario: Claim filing flow
- **WHEN** the farmer taps "File Claim" on an active policy
- **THEN** a form is presented to select the policy, describe the issue, attach at least 1 photo, and submit

#### Scenario: Claim requires photo and description
- **WHEN** the farmer attempts to submit a claim without a photo or description
- **THEN** a validation error is shown requiring at least 1 photo and a text description

#### Scenario: Claim status tracker
- **WHEN** the farmer views a filed claim
- **THEN** a status tracker shows the current stage: pending, under review, approved, or rejected

#### Scenario: Claim status change notification
- **WHEN** a claim status changes (e.g., from "under review" to "approved")
- **THEN** a notification card appears on the home screen with the updated status

#### Scenario: Policy renewal reminder
- **WHEN** a policy premium due date is within 7 days
- **THEN** a reminder card is shown on the insurance screen and the home screen
