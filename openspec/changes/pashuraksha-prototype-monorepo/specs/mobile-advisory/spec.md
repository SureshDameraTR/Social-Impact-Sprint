## ADDED Requirements

### Requirement: Advisory feed with seasonal tips and government announcements
The mobile app SHALL provide a scrollable advisory feed with cards for seasonal animal care tips, feeding advice, breeding guidance, and government scheme announcements. The feed SHALL be filterable by species and category, support bilingual display, and show source badges.

#### Scenario: Farmer opens advisory feed
- **WHEN** the farmer opens the advisory screen
- **THEN** the latest tips are displayed filtered by the farmer's registered animal species

#### Scenario: Filter by species
- **WHEN** the farmer selects a species filter (e.g., cattle, buffalo, goat, sheep, poultry)
- **THEN** only advisory cards relevant to the selected species are shown

#### Scenario: Filter by category
- **WHEN** the farmer selects a category filter (health, feeding, breeding, government)
- **THEN** only advisory cards matching the selected category are shown

#### Scenario: Bilingual toggle per card
- **WHEN** the farmer taps the language toggle on an advisory card
- **THEN** the card content switches between Kannada and English

#### Scenario: Source badges on cards
- **WHEN** an advisory card is displayed
- **THEN** it shows a source badge indicating the origin: "ICAR", "KMF", "NABARD", or "Community"

#### Scenario: Government scheme announcement
- **WHEN** a new government scheme is announced
- **THEN** a highlighted card appears in the feed with an "Apply Now" link to the scheme details

#### Scenario: Species-specific tip visibility
- **WHEN** a tip is tagged as species-specific (e.g., poultry only)
- **THEN** only farmers who own that species see the tip in their feed

#### Scenario: Advisory card detail view
- **WHEN** the farmer taps an advisory card
- **THEN** the full advisory content is displayed with source link and publish date
