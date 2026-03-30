## ADDED Requirements

### Requirement: Sell tab in mobile app
The farmer mobile app SHALL include a Sell tab for recording product sales with multiple categories.

#### Scenario: Farmer navigates to Sell tab
- **GIVEN** an authenticated farmer on the home screen
- **WHEN** they tap the Sell (ಮಾರಾಟ) tab in the bottom navigation
- **THEN** they see a product category grid with 4 large cards: Milk (ಹಾಲು), Eggs (ಮೊಟ್ಟೆ), Goat/Sheep (ಆಡು/ಕುರಿ), Manure (ಗೊಬ್ಬರ)

#### Scenario: Farmer records a milk sale
- **WHEN** the farmer taps the Milk card, enters quantity using +/- controls or numpad
- **THEN** the price auto-calculates based on local APMC rates (₹30/L default), and they can tap "Record Sale" (ಮಾರಾಟ ದಾಖಲಿಸಿ)

#### Scenario: Farmer uses voice to enter sell quantity
- **WHEN** the farmer taps the mic button on the sell screen and says "Hattu liter haalu" (10 liters milk)
- **THEN** the Sarvam AI STT parses the Kannada input and populates the quantity field with 10

#### Scenario: Farmer views sale history
- **WHEN** the farmer taps "History" (ಇತಿಹಾಸ) on the sell screen
- **THEN** they see recent sales listed with date, product icon, quantity, and total amount
