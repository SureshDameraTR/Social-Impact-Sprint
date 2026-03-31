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

### Requirement: Multi-language expansion
The app SHALL support 7 languages via i18next: Kannada (kn), English (en), Hindi (hi), Telugu (te), Tamil (ta), Marathi (mr), and Kannada remains the default. Language selection SHALL persist across app restarts.

#### Scenario: Farmer switches to Hindi
- **WHEN** the farmer selects Hindi in the language settings
- **THEN** all UI text switches to Hindi immediately and the preference is persisted

#### Scenario: App remembers language preference
- **WHEN** the app is reopened after being closed
- **THEN** the previously selected language is restored without prompting

### Requirement: Home screen weather card
The home screen SHALL display a weather card showing today's weather for the farmer's district with temperature, humidity, rainfall probability, and a heat stress indicator for livestock.

#### Scenario: Weather card shows current conditions
- **WHEN** the farmer opens the home screen
- **THEN** a weather card displays: temperature, humidity, rainfall chance, wind speed, and a livestock heat stress level (Normal / Caution / Danger) based on THI (Temperature-Humidity Index)

#### Scenario: Heat stress danger triggers advisory
- **WHEN** THI exceeds 78 (danger zone for livestock)
- **THEN** the weather card shows a red "Heat Stress Danger" badge with advisory text: "Provide shade, extra water, and reduce movement"

### Requirement: Vaccination reminder cards
The home screen SHALL display upcoming and overdue vaccination cards for all of the farmer's animals.

#### Scenario: Upcoming vaccination shown on home screen
- **WHEN** an animal has a vaccination due within 7 days
- **THEN** a yellow reminder card appears on the home screen: "Vaccination due: [vaccine_name] for [animal_name] on [date]"

#### Scenario: Overdue vaccination shown as urgent
- **WHEN** an animal has a vaccination past its due date
- **THEN** a red urgent card appears on the home screen: "OVERDUE: [vaccine_name] for [animal_name] — [days] days overdue"

### Requirement: Community alert banner
The home screen SHALL display a banner for nearby disease alerts based on the farmer's GPS location.

#### Scenario: Active community alert shown
- **WHEN** a community disease alert exists within 10km of the farmer's location
- **THEN** a red/orange banner appears at the top of the home screen: "[disease] reported near [village] — tap for details" with distance and precaution advice

#### Scenario: No alerts results in no banner
- **WHEN** no community alerts exist within 10km
- **THEN** no alert banner is displayed on the home screen

### Requirement: Smart Farm access
The home screen header SHALL include an icon linking to the IoT/Smart Farm mockup screen for farmers with connected devices.

#### Scenario: Farmer with IoT devices sees Smart Farm icon
- **WHEN** the farmer has at least one registered IoT device
- **THEN** a "Smart Farm" icon appears in the home screen header that navigates to the Smart Farm dashboard showing device status, sensor readings, and automated alerts

#### Scenario: Farmer without IoT devices
- **WHEN** the farmer has no registered IoT devices
- **THEN** the Smart Farm icon is hidden or shows a "Coming Soon" state
