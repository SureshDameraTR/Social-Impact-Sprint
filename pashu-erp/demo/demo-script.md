# PashuRaksha Demo Script — April 27, 2026
Duration: ~15 minutes | Presenter: Suresh Damera

## Pre-Demo Setup (5 min before)
1. Start Docker: `docker compose up -d db`
2. Start API: `just dev` (verify http://localhost:8000/docs loads)
3. Re-seed if needed: `just seed`
4. Open mobile app on Android emulator
5. Open admin dashboard at http://localhost:3000

## Scenario 1: Farmer Registration (2 min)
**Story**: Lakshmi Devi, a dairy farmer from Mysore, registers on PashuRaksha

1. Open app → Splash screen with PashuRaksha logo
2. Tap "Login" → Enter phone: +919900000002
3. Enter OTP: 123456
4. Show Home screen — "ನನ್ನ ಪ್ರಾಣಿಗಳು" (My Animals)
5. Point out: Kannada UI, large icons, species filter chips
6. Tap "+" to add animal → Show Pashu Aadhaar field
7. **Key message**: "Phone-based auth, no passwords, farmers just need their phone"

## Scenario 2: Record Milk via Kannada Voice (2 min)
**Story**: Lakshmi records morning milk yield using voice

1. Tap "ಹಾಲು" (Milk) tab
2. Select cow "Lakshmi" from picker
3. Select "ಬೆಳಿಗ್ಗೆ" (Morning)
4. Tap mic button → Pulsing animation
5. Voice recognition shows: "ಐದು ಲೀಟರ್" → 5L auto-populated
6. Tap "ಉಳಿಸಿ" (Save)
7. **Key message**: "Kannada voice input — no typing needed for low-literacy users"

## Scenario 3: View Milk History Chart (1 min)
**Story**: Lakshmi checks her cow's milk production trend

1. From Milk tab, tap "ಇತಿಹಾಸ" (History)
2. Show 30-day bar chart with morning/evening yields
3. Toggle between 7/14/30 day views
4. Point out yield variance (realistic 5-8L/day for HF Cross)
5. **Key message**: "Visual analytics even for farmers who can't read spreadsheets"

## Scenario 4: Health Check with AI Triage (2 min)
**Story**: Lakshmi notices her cow Gowri is unwell

1. Tap "ಆರೋಗ್ಯ" (Health) tab
2. Select cow "Gowri"
3. Tap symptoms: fever, swollen_udder, reduced_milk
4. Submit → Triage card appears: HIGH RISK (red)
5. Shows: "Probable: Mastitis" with recommended action
6. "Isolate, apply cold compress, consult veterinarian"
7. **Key message**: "56 disease rules from ICAR/NDDB — instant triage without a vet visit"

## Scenario 5: Admin Dashboard (2 min)
**Story**: RDO admin views the program overview

1. Switch to admin dashboard (http://localhost:3000)
2. Show 6 stat cards: Farmers, Animals, Today's Milk, Alerts, Revenue, Sellers
3. Show 30-day milk collection chart
4. Show GIS map with disease alert markers (Karnataka)
5. Click through: Farmers list, Animals list, Health Alerts
6. **Key message**: "Real-time visibility for program administrators"

## Scenario 6: Full Kannada UI (1 min)
**Story**: Every screen works in Kannada

1. Return to mobile app
2. Scroll through tabs showing all Kannada labels
3. Go to Profile → Show language toggle (Kannada / English)
4. Toggle to English briefly, then back to Kannada
5. **Key message**: "Kannada-first, not English-translated"

## Scenario 7: Sell Products & Track Revenue (2 min)
**Story**: Lakshmi sells 10L milk and 20 eggs at the market

1. Tap "ಮಾರಾಟ" (Sell) tab
2. Select "ಹಾಲು" (Milk) → quantity: 10L → auto-price: Rs 31.50/L → Total: Rs 315
3. Tap "ಮಾರಾಟ ದಾಖಲಿಸಿ" (Record Sale)
4. Select "ಮೊಟ್ಟೆ" (Eggs) → quantity: 20 → auto-price: Rs 6/each → Total: Rs 120
5. Record sale
6. Show recent sales list
7. **Key message**: "APMC market rates auto-applied — farmers know fair price"

## Scenario 8: Income Dashboard (1 min)
**Story**: Lakshmi views her weekly earnings

1. Tap "ಆದಾಯ" (Income) tab
2. Show weekly earnings: Rs 2,450 (hero card)
3. Show product breakdown: Milk 65%, Eggs 20%, Manure 15%
4. Show "Apply for Loan" CTA
5. **Key message**: "Digital income proof for NABARD/SHG loan applications"

## Scenario 9: Smart Farm / IoT Vision (1 min)
**Story**: Future capability preview

1. Tap Smart Farm icon in header
2. Show GPS map placeholder with animal markers
3. Show device cards: RFID, Milk Meter, GPS Collar, Smart Feeder
4. Point out "Phase 2 — Coming Soon" banner
5. **Key message**: "Platform ready for IoT integration when hardware is available"

## Closing (1 min)
- 135+ files, 21 API endpoints, 26 mobile screens, 10 admin pages
- Built for Karnataka pilot, expandable to all India
- Multi-species: cattle, goats, sheep, poultry
- Offline-first architecture planned for Phase 2
- Budget: Rs 50-75 lakh for full production build
