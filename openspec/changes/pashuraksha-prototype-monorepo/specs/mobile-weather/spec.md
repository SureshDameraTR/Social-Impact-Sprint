## ADDED Requirements

### Requirement: Weather information screen for farmers
The mobile app SHALL provide weather information relevant to livestock management. The home screen SHALL display a weather summary card, and a dedicated weather screen SHALL show a 5-day forecast with livestock impact notes. Heat stress alerts SHALL trigger prominent warnings.

#### Scenario: Home screen weather card
- **WHEN** the farmer opens the home screen
- **THEN** a weather card displays today's temperature, humidity, heat stress indicator, and rain probability

#### Scenario: Weather detail screen with 5-day forecast
- **WHEN** the farmer opens the weather detail screen
- **THEN** a 5-day forecast is displayed with weather icons, daily highs/lows, and livestock impact notes for each day

#### Scenario: Alert history on weather screen
- **WHEN** the farmer scrolls down on the weather detail screen
- **THEN** a list of recent weather alerts and their timestamps is displayed

#### Scenario: Heat stress warning banner
- **WHEN** the temperature exceeds 40 degrees Celsius
- **THEN** a red banner is shown on the home screen with a livestock care advisory (shade, water, reduced work)

#### Scenario: Heat stress banner dismissal
- **WHEN** the temperature drops below the heat stress threshold
- **THEN** the red banner is automatically removed from the home screen

#### Scenario: Kannada voice weather summary
- **WHEN** the farmer taps the voice button on the weather screen
- **THEN** the weather summary is read aloud in Kannada using Sarvam TTS

#### Scenario: Weather data refresh
- **WHEN** the farmer pulls to refresh on the weather screen
- **THEN** the latest weather data is fetched and displayed
