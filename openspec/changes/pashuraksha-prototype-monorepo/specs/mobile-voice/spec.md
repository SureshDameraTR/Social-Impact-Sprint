## ADDED Requirements

### Requirement: Sarvam AI Kannada STT integration for milk recording
The mobile app SHALL integrate Sarvam AI Saaras V3 for Kannada speech-to-text. A mic button on the milk recording screen SHALL capture audio and convert Kannada number words to numeric values.

#### Scenario: Farmer says "Aidu liter" in Kannada
- **WHEN** the farmer taps the mic button and says "ಐದು ಲೀಟರ್" (Aidu liter)
- **THEN** the STT returns "ಐದು ಲೀಟರ್", the parser extracts "5", and the milk quantity field is populated with 5.0

#### Scenario: Farmer says "Mooru liter"
- **WHEN** the farmer says "ಮೂರು ಲೀಟರ್" (Mooru liter)
- **THEN** the quantity field is populated with 3.0

#### Scenario: Voice recognition fails
- **WHEN** the STT returns low confidence or unrecognized audio
- **THEN** the app shows a Kannada message "Voice not recognized, please try again or enter manually" and the manual numpad remains available

### Requirement: Kannada number word parser
The app SHALL include a parser that converts Kannada number words (ಒಂದು=1, ಎರಡು=2, ಮೂರು=3, ನಾಲ್ಕು=4, ಐದು=5, ಆರು=6, ಏಳು=7, ಎಂಟು=8, ಒಂಬತ್ತು=9, ಹತ್ತು=10) and decimal patterns to numeric values.

#### Scenario: Parser handles compound numbers
- **WHEN** the STT returns "ಐದೂವರೆ" (five and a half)
- **THEN** the parser returns 5.5

#### Scenario: Parser handles digits mixed with words
- **WHEN** the STT returns "5 ಲೀಟರ್"
- **THEN** the parser returns 5.0

### Requirement: Mic button with recording indicator
The mic button SHALL show a visual recording indicator (pulsing animation) while capturing audio. Recording SHALL auto-stop after 5 seconds of silence or 10 seconds maximum.

#### Scenario: Recording feedback
- **WHEN** the farmer taps the mic button
- **THEN** a pulsing red indicator appears and the button label changes to "Listening..." in Kannada
