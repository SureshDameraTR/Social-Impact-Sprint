## ADDED Requirements

### Requirement: Farmer authentication flow
The mobile app SHALL provide a phone number + OTP login screen. On successful auth, the JWT token SHALL be stored in `expo-secure-store`. The app SHALL redirect to the home screen after login.

#### Scenario: Farmer logs in with OTP
- **WHEN** a farmer enters phone number and correct OTP
- **THEN** the token is stored securely and the farmer sees the home screen with their animals

#### Scenario: Token persistence across app restarts
- **WHEN** the app is reopened after being closed
- **THEN** the stored token is used to auto-login (if not expired)

### Requirement: Animal management screens
The app SHALL display a "My Animals" list on the home tab with large cards showing animal photo/icon, name, species, and health status color (green/yellow/red). Farmers SHALL be able to add new animals and view animal details.

#### Scenario: Farmer views animal list
- **WHEN** the farmer opens the home tab
- **THEN** large animal cards are displayed with 64px+ species icons, name, breed, and color-coded health status

#### Scenario: Farmer adds a new animal
- **WHEN** the farmer taps "Add Animal" and fills in name, species (icon picker), breed, and optional Pashu Aadhaar
- **THEN** the animal is created via API and appears in the list

#### Scenario: Farmer views animal detail
- **WHEN** the farmer taps an animal card
- **THEN** the detail screen shows animal info, health timeline, and vaccination schedule

### Requirement: Milk recording with AM/PM toggle
The app SHALL provide a milk recording screen with animal picker, large numpad for quantity entry, and AM/PM shift toggle.

#### Scenario: Farmer records milk manually
- **WHEN** the farmer selects an animal, enters "5" on the numpad, selects "AM", and taps save
- **THEN** a milk yield record is created via API and a success confirmation is shown

### Requirement: Milk history bar chart
The app SHALL display a bar chart of milk yield history for the selected period (7/14/30 days).

#### Scenario: Farmer views 30-day milk chart
- **WHEN** the farmer navigates to the milk history screen and selects "30 days"
- **THEN** a bar chart displays daily milk totals with `react-native-gifted-charts`

### Requirement: Health event logging with risk alerts
The app SHALL allow farmers to log health events by selecting symptoms from an icon-based picker. After submission, the app SHALL display the rule-based triage result with color-coded risk level.

#### Scenario: Farmer logs high-risk symptoms
- **WHEN** the farmer logs symptoms "fever" + "nasal discharge" for an animal
- **THEN** the API triage result is displayed as a red alert card: "High risk — consult vet immediately"

#### Scenario: Farmer logs low-risk symptoms
- **WHEN** the farmer logs only "reduced appetite"
- **THEN** the triage result shows a green/yellow card: "Monitor for 48 hours"

### Requirement: Kannada-first i18n
The app SHALL support Kannada (kn) as the primary language and English (en) as secondary. The language toggle SHALL be accessible from settings. All UI text SHALL use Noto Sans Kannada bundled as a custom font.

#### Scenario: App defaults to Kannada
- **WHEN** the app is opened for the first time
- **THEN** all UI text is displayed in Kannada

#### Scenario: User switches to English
- **WHEN** the farmer toggles language to English in settings
- **THEN** all UI text switches to English immediately

### Requirement: Bottom tab navigation with max 2-tap depth
The app SHALL use bottom tab navigation with maximum 4-5 tabs. Any core action SHALL be reachable within 2 taps from the home screen. No hamburger menus.

#### Scenario: Core navigation structure
- **WHEN** the app is loaded
- **THEN** bottom tabs show: Home (animals), Milk, Health, Profile — each with a large icon and Kannada label

### Requirement: Large touch targets and accessible design
All interactive elements SHALL have minimum 48dp touch targets. Icons SHALL be 64px+ pictographic. Color-coded status SHALL use green (healthy), yellow (watch), red (urgent).

#### Scenario: Touch targets on budget Android
- **WHEN** the app runs on a 5-inch Android device with 2GB RAM
- **THEN** all buttons and interactive elements are easily tappable without precision
