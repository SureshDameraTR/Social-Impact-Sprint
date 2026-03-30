# PashuRaksha i18n & Multilingual Implementation Guide

> Research compiled: 2026-03-30
> Target: Rural/agricultural users in Karnataka, India
> Primary language: Kannada (kn-IN) | Secondary: English (en-IN)
> Expansion languages: Telugu, Tamil, Hindi, Marathi, Malayalam

---

## Table of Contents

1. [Kannada Language Specifics](#1-kannada-language-specifics)
2. [Indian Language i18n Best Practices](#2-indian-language-i18n-best-practices)
3. [Voice-First for Indian Languages](#3-voice-first-for-indian-languages)
4. [Expansion Languages](#4-expansion-languages)
5. [Text-to-Speech for Farming Content](#5-text-to-speech-for-farming-content)
6. [Implementation Patterns](#6-implementation-patterns)
7. [Government Language Requirements](#7-government-language-requirements)
8. [PashuRaksha-Specific Recommendations](#8-pashuraksha-specific-recommendations)

---

## 1. Kannada Language Specifics

### 1.1 Unicode Rendering on Budget Android

Kannada script (Unicode block U+0C80-U+0CFF) was first encoded in Unicode 1.0 and has undergone refinements since, including glyph changes for Vocalic L/LL as recently as 2023-2024.

**Key challenges on budget Android devices:**

| Challenge | Impact | Mitigation |
|-----------|--------|------------|
| Incomplete shaping engine on Android < 8 | Broken conjuncts, missing ligatures | Bundle Noto Sans Kannada as a fallback font |
| Manufacturer font fragmentation | Inconsistent rendering across Xiaomi, Samsung, Realme | Test on 3+ budget devices; never rely solely on emulators |
| Slow software updates on budget phones | Outdated HarfBuzz shaping engine | Target minimum Android 8.0 (API 26) where Kannada shaping is stable |
| Complex conjunct rendering | Higher GPU/CPU cost for text layout | Limit text-heavy screens; prefer icons + short labels |
| Glyph display as boxes/question marks | Unreadable text on very old devices | Detect missing font support and show English fallback with warning |

**Recommendation for PashuRaksha:** Set minimum Android version to 8.0 (Oreo). This covers 95%+ of active devices in India while ensuring stable Kannada rendering. Bundle Noto Sans Kannada as an app-level fallback font.

### 1.2 Font Requirements

**Noto Sans Kannada** (Google's universal font):
- 655 glyphs, 11 OpenType features, 164 characters from 5 Unicode blocks
- Multiple weights (Thin to Black) and widths
- Well-proportioned spacing, balanced x-height, distinct character differentiation
- Free, open-source (OFL license)
- Available on Google Fonts: https://fonts.google.com/noto/specimen/Noto+Sans+Kannada

**Noto Sans Kannada vs. system fonts:**

| Aspect | Noto Sans Kannada (bundled) | System fonts |
|--------|---------------------------|--------------|
| Consistency | Identical across all devices | Varies by manufacturer |
| App size | +200-400KB per weight | Zero overhead |
| Rendering quality | Excellent, all conjuncts | May have gaps on older devices |
| Update control | You control the version | Depends on OS updates |

**Recommendation:** Use system font as primary (most budget devices Android 8+ have adequate Kannada support), bundle Noto Sans Kannada Regular + Bold (~400KB total) as fallback. Use Google's **Anek** multi-script font family if you need visual consistency across Kannada, Telugu, Tamil, Hindi, and Malayalam.

### 1.3 Text Expansion Ratios

No published industry-standard ratio exists for English-to-Kannada specifically. Based on research and general Indic language patterns:

| Dimension | Expansion Factor | Notes |
|-----------|-----------------|-------|
| Character count | 0.8-1.2x | Kannada can be more compact in character count |
| Horizontal width | 1.2-1.4x | Kannada glyphs are wider than Latin characters |
| Vertical height | 1.3-1.5x | Conjuncts, vowel signs above/below base characters |
| Line height needed | 1.4-1.6x | Complex conjuncts (ottaksharas) need extra vertical space |
| Button/label text | 1.2-1.5x | Plan for 50% wider buttons minimum |

**Practical design rules for PashuRaksha:**
- Never use fixed-width buttons -- use `flex` or `minWidth` with padding
- Set `lineHeight` multiplier to at least 1.5 for Kannada text
- Test every screen with real Kannada content, not placeholders
- Use `numberOfLines` + `ellipsizeMode` for overflow protection

### 1.4 Kannada Voice Recognition Accuracy

| Provider | Kannada STT | Accuracy (field) | Code-switching | Agricultural terms | Pricing |
|----------|-------------|-------------------|----------------|-------------------|---------|
| **Sarvam AI (Saaras V3)** | Yes (kn-IN) | ~82% in noisy rural settings | Moderate | Fine-tunable (enterprise) | Pay-per-use API |
| **Google Cloud STT (Chirp 3)** | Yes (kn-IN) | Good for clear speech, degrades with noise/dialect | Limited | No domain customization | $0.006/15s |
| **Bhashini (Gov)** | Yes (kn-IN) | Varies by model | Limited | No domain specialization | Free for Indian developers |
| **Microsoft Azure** | Yes (kn-IN) | Good general | HD voices support multilingual | Custom model training available | $1/audio hour |
| **Soniox** | Yes | Good | Auto-detects mid-sentence switching | No domain focus | Enterprise pricing |
| **Reverie** | Yes | Designed for Indian accents | Handles code-mixing natively | No domain focus | Enterprise pricing |

**Key finding:** Sarvam AI's Bulbul-v2 achieved 82% accuracy in agricultural market settings in rural Karnataka with significant background noise. This is the most relevant benchmark for PashuRaksha's use case.

### 1.5 Common Kannada Agricultural Terminology

Essential vocabulary for PashuRaksha that must be accurately recognized and translated:

| English | Kannada | Transliteration | Category |
|---------|---------|-----------------|----------|
| Agriculture | ಕೃಷಿ | Krushi | General |
| Animal husbandry | ಪಶುಪಾಲನೆ | Pashupaalane | General |
| Dairy farming | ಹೈನುಗಾರಿಕೆ | Hainugaarike | Dairy |
| Cow | ಹಸು | Hasu | Animal |
| Buffalo | ಎಮ್ಮೆ | Emme | Animal |
| Goat | ಮೇಕೆ | Meke | Animal |
| Sheep | ಕುರಿ | Kuri | Animal |
| Milk | ಹಾಲು | Haalu | Dairy |
| Liter | ಲೀಟರ್ | Leetar | Unit |
| Vaccination | ಲಸಿಕೆ | Lasike | Health |
| Fever | ಜ್ವರ | Jvara | Health |
| Feed/fodder | ಮೇವು | Mevu | Feed |
| Breed | ತಳಿ | Tali | Animal |
| Calf | ಕರು | Karu | Animal |
| Veterinarian | ಪಶುವೈದ್ಯ | Pashuvaidya | Health |
| Market/sale | ಮಾರಾಟ | Maaraata | Commerce |
| Income | ಆದಾಯ | Aadaaya | Finance |
| Loan | ಸಾಲ | Saala | Finance |
| Self-help group | ಸ್ವ-ಸಹಾಯ ಗುಂಪು | Sva-sahaaya gumpu | SHG |
| Government scheme | ಸರ್ಕಾರಿ ಯೋಜನೆ | Sarkaari yojane | Scheme |
| Poultry | ಕೋಳಿ ಕೃಷಿ | Koli krushi | Animal |
| Sericulture | ರೇಷ್ಮೆ ಕೃಷಿ | Reshme krushi | Farming |
| Beekeeping | ಜೇನುಸಾಕಣೆ | Jenusaakane | Farming |
| Land | ಭೂಮಿ | Bhoomi | General |

**Kannada number words (critical for voice milk recording):**

| Number | Kannada | Transliteration |
|--------|---------|-----------------|
| 1 | ಒಂದು | Ondu |
| 2 | ಎರಡು | Eradu |
| 3 | ಮೂರು | Mooru |
| 4 | ನಾಲ್ಕು | Naalku |
| 5 | ಐದು | Aidu |
| 6 | ಆರು | Aaru |
| 7 | ಏಳು | Elu |
| 8 | ಎಂಟು | Entu |
| 9 | ಒಂಬತ್ತು | Ombattu |
| 10 | ಹತ್ತು | Hattu |
| Half | ಅರ್ಧ | Ardha |
| Quarter | ಕಾಲು | Kaalu |
| Five and half | ಐದೂವರೆ | Aiduvare |

### 1.6 Dialectal Variations Across Karnataka

Karnataka has notable dialectal variation that affects speech recognition:

| Region | Dialect characteristics | Impact on STT |
|--------|------------------------|---------------|
| Old Mysuru (Mysuru, Mandya, Hassan) | "Standard" literary Kannada, softer pronunciation | Best recognition accuracy |
| Bengaluru urban | Heavy English code-switching ("Kanglish") | Needs code-switching support |
| North Karnataka (Dharwad, Belgaum, Bidar) | Distinct vowel shifts, vocabulary differences | May need model fine-tuning |
| Coastal (Dakshina Kannada, Uttara Kannada) | Influenced by Tulu, Konkani; different intonation | Lower accuracy expected |
| Hyderabad-Karnataka (Gulbarga, Raichur) | Urdu/Hindi influence, distinct vocabulary | May need specific training data |

**Recommendation:** Start with standard Mysuru-Bengaluru dialect recognition. Collect field audio samples from target districts to evaluate accuracy before expanding.

---

## 2. Indian Language i18n Best Practices

### 2.1 How Successful Indian Apps Handle Multi-Language

**PhonePe / Indus Appstore:**
- Native Android app store available in English + 12 Indian languages
- Localized app discovery and culturally adapted visual content
- Language selection persisted in user profile

**WhatsApp India:**
- Supports 12+ Indian languages for UI
- Multilingual AI bots handle code-switching (Hinglish) natively
- Voice notes preferred over typing in Tier 2-3 cities (critical insight for PashuRaksha)
- Memory-enabled bots report 35-45% higher retention vs stateless bots

**Key patterns observed across successful Indian apps:**
1. Language selection on first launch (large, visible picker)
2. Language preference persisted across sessions and devices
3. Voice input preferred over typing for regional languages
4. Mixed-script content (English numbers in regional text) is normal and expected
5. Google Play dominates (95% market share in India) -- prioritize Android

### 2.2 i18n Library Comparison for Expo/React Native

| Feature | i18next + react-i18next | expo-localization | react-native-localize |
|---------|------------------------|-------------------|-----------------------|
| **Role** | Full i18n framework (translations, plurals, interpolation) | Device locale detection (Expo) | Device locale detection (bare RN) |
| **Indian language support** | Any language via JSON files | Detects device locale (hi, ta, te, kn, etc.) | Detects device locale |
| **Pluralization** | Full ICU support | N/A | N/A |
| **Interpolation** | `{{name}}` syntax | N/A | N/A |
| **Namespace support** | Yes (load per feature) | N/A | N/A |
| **Fallback chains** | `kn` -> `en` configurable | N/A | N/A |
| **Dynamic switching** | Yes, without restart | N/A | N/A |
| **Downloads/week** | 6.3M+ | Part of Expo SDK | 1M+ |
| **Best for** | Translation logic & rendering | Detecting user's preferred language in Expo | Detecting in bare RN |

**Recommended stack for PashuRaksha:**
```
expo-localization  (device locale detection)
  + i18next         (translation engine)
  + react-i18next   (React bindings)
  + AsyncStorage     (language preference persistence)
```

Install: `npx expo install expo-localization react-i18next i18next`

### 2.3 Dynamic Language Switching Without App Restart

```typescript
// i18n.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import * as Localization from 'expo-localization';
import AsyncStorage from '@react-native-async-storage/async-storage';

import kn from './locales/kn.json';
import en from './locales/en.json';

const LANGUAGE_KEY = '@pashuraksha/language';

const languageDetector = {
  type: 'languageDetector' as const,
  async: true,
  detect: async (callback: (lang: string) => void) => {
    const saved = await AsyncStorage.getItem(LANGUAGE_KEY);
    if (saved) return callback(saved);
    const deviceLang = Localization.getLocales()[0]?.languageCode;
    callback(deviceLang === 'kn' ? 'kn' : 'en');
  },
  init: () => {},
  cacheUserLanguage: async (lang: string) => {
    await AsyncStorage.setItem(LANGUAGE_KEY, lang);
  },
};

i18n
  .use(languageDetector)
  .use(initReactI18next)
  .init({
    resources: { kn: { translation: kn }, en: { translation: en } },
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
    react: { useSuspense: false },
  });

export default i18n;

// Switching language (no restart needed):
// i18n.changeLanguage('kn');
```

### 2.4 Mixed-Script Content

Rural Indian users commonly see and expect:
- English numerals in Kannada text: "ಹಾಲು: 5 ಲೀಟರ್" (Milk: 5 liters)
- English brand names in Kannada sentences
- Phone numbers always in Latin digits

**Rules for PashuRaksha:**
1. Always use Latin numerals (1, 2, 3) -- NOT Kannada numerals (೧, ೨, ೩)
2. Keep units in context: "5 ಲೀ." or "₹500"
3. Keep technical terms in English when no common Kannada equivalent exists
4. Currency always as "₹" prefix with Latin digits

### 2.5 Date/Time/Currency Formatting

```typescript
// Use Intl API (supported in Hermes engine on Expo)
const formatDate = (date: Date) =>
  new Intl.DateTimeFormat('kn-IN', {
    day: 'numeric', month: 'long', year: 'numeric'
  }).format(date);
// Output: "30 ಮಾರ್ಚ್ 2026"

const formatCurrency = (amount: number) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency', currency: 'INR'
  }).format(amount);
// Output: "₹5,000.00"
// Note: Use 'en-IN' for currency to keep Latin digits

const formatTime = (date: Date) =>
  new Intl.DateTimeFormat('kn-IN', {
    hour: 'numeric', minute: 'numeric', hour12: true
  }).format(date);
// Output: "ಬೆಳಿಗ್ಗೆ 6:30" (morning 6:30)
```

**Important:** Use `en-IN` locale for currency and numbers to ensure Latin digits. Use `kn-IN` for month/day names when showing dates in Kannada UI.

### 2.6 Numeral Systems

| System | Example | When to use |
|--------|---------|-------------|
| Latin digits (123) | ₹500, 5 liters, phone numbers | Always -- this is what rural users expect |
| Kannada numerals (೧೨೩) | Rarely used in practice | Avoid in app UI -- low recognition among rural users |

Research shows that even native Kannada speakers use Latin digits in daily life (bank accounts, phone numbers, market transactions). Kannada numerals are primarily used in literary/academic contexts.

---

## 3. Voice-First for Indian Languages

### 3.1 Sarvam AI -- Capabilities & Limitations

**Current models (as of early 2026):**

| Model | Capability | Languages | Key features |
|-------|-----------|-----------|--------------|
| **Saaras V3** (ASR) | Speech-to-Text | 11 Indian languages including Kannada | 19.31% WER on IndicVoices; trained on 1M+ hours |
| **Bulbul V3** (TTS) | Text-to-Speech | 11 Indian languages including Kannada | Natural prosody, emotion detection |
| **Sarvam-1** (LLM) | Text generation | 10 Indian languages | Foundation model for Indian languages |

**Strengths for PashuRaksha:**
- 82% accuracy in noisy rural Karnataka market settings (field-tested)
- Trained on 25,000+ hours of diverse acoustic environments (rural households, markets, moving vehicles)
- Enterprise tier allows custom fine-tuning for agricultural terminology
- On-premises/private cloud deployment option for data sovereignty
- Active partnership with Tamil Nadu for agricultural AI assistant (Vivasaya Nanban)

**Limitations:**
- Code-switching (Kannada-English) accuracy not yet benchmarked publicly
- No published dialectal accuracy breakdown across Karnataka regions
- Enterprise tier pricing not publicly available
- Fine-tuning requires substantial domain-specific audio data

**API integration (already specified in PashuRaksha mobile-voice spec):**
The existing spec correctly targets Saaras V3 for milk recording voice input with Kannada number word parsing.

### 3.2 Google Cloud Speech-to-Text

**Capabilities:**
- Supports Kannada (kn-IN) via Chirp 3 foundation model
- Trained on millions of hours of audio, billions of text sentences across 100+ languages
- Self-supervised learning approach

**For PashuRaksha:**
- Good as a fallback provider if Sarvam is unavailable
- Better for clear, quiet environments (less suited for field use)
- No domain-specific agricultural customization
- Code-switching support is limited compared to India-focused providers
- Pricing: ~$0.006 per 15 seconds

### 3.3 Bhashini (Government of India)

**What it is:** India's Digital Public Infrastructure (DPI) for language AI, under MeitY. Hosts 300+ AI models for ASR, MT, TTS, OCR, and transliteration across all 22 scheduled languages.

**Capabilities:**
- Pipeline API: Chain ASR + Machine Translation + TTS in a single call
- Supports speech-to-speech translation (Kannada speech -> English text -> English speech, or any combination)
- Open-source data platform (ULCA) with standardized datasets
- Powers PM Kisan, UIDAI, eSanjeevani, Indian Railways

**API access:**
- Free for Indian developers/startups
- REST API with pipeline search + pipeline execution calls
- Accepts Base64-encoded WAV audio (does NOT support WebM directly)
- No built-in profanity filter
- Documentation: https://bhashini.gitbook.io/bhashini-apis

**For PashuRaksha:**
- Excellent for machine translation (Kannada <-> English for admin dashboard)
- Free tier makes it viable for non-profit/social impact projects
- Can serve as fallback STT provider
- Government alignment strengthens compliance narrative

**Limitations:**
- Audio must be WAV format (need client-side conversion from WebM/Opus)
- Quality varies by model -- must test specific pipelines
- Latency may be higher than commercial APIs

### 3.4 Microsoft Azure Speech

**Kannada support:**
- STT: `kn-IN` locale supported
- TTS: 6 Kannada (India) voices available (male + female)
- February 2025: New HD voices (Aarti, Arjun) for Hindi/English with emotion detection
- Custom model training available for domain-specific vocabulary

**For PashuRaksha:**
- Good quality but not India-specialized like Sarvam
- HD voices with emotion detection could enhance TTS for advisory content
- Custom STT model training possible but requires significant data
- Pricing: ~$1/audio hour for STT

### 3.5 Accuracy Benchmarks Summary

| Provider | General Kannada WER | Noisy rural setting | Agricultural terms | Code-switching |
|----------|--------------------|--------------------|-------------------|----------------|
| Sarvam Saaras V3 | ~19% (IndicVoices) | ~18% error (82% accuracy) | Fine-tunable | Moderate |
| Google Chirp 3 | ~20-25% estimated | Higher error rate | No customization | Limited |
| Bhashini (best model) | Varies by model | Unknown | No specialization | Limited |
| Azure Speech | ~20-25% estimated | Unknown | Custom training available | HD voices support |

### 3.6 Handling Code-Switching (Kannada-English)

Code-switching is pervasive in Karnataka, especially in urban/semi-urban areas. A farmer might say:
- "ನನ್ನ cow ಗೆ fever ಇದೆ" ("My cow has fever" -- mixing English nouns)
- "5 liters haalu" ("5 liters milk" -- English quantity, Kannada noun)

**Technical approaches:**

1. **Common script transliteration:** Transliterate all text to a common script (Devanagari) to create unified phonemic representation, then use fine-tuned Wav2Vec 2.0. Shown to significantly outperform baseline models.

2. **Word-level language identification:** Transformer models for Kannada-English (CoLI-Kanglish dataset) achieve F1-score of 0.84 at word level.

3. **Commercial solutions:**
   - Soniox: Auto-detects language switching mid-sentence, no configuration needed
   - Reverie: Native code-mixing support designed for Indian markets
   - Sarvam: Handles common code-switching patterns

**Recommendation for PashuRaksha:** For the milk recording voice feature, code-switching is less of an issue since input is primarily numbers + unit words. For future advisory/chat features, prioritize Sarvam or Reverie which handle Indian code-switching natively.

---

## 4. Expansion Languages

### 4.1 Telugu (te-IN)

| Aspect | Details |
|--------|---------|
| Script | Telugu (U+0C00-U+0C7F), highly rounded and looped |
| Rendering challenges | Reph sign only supported in Noto Sans Telugu; Chandrabindu character (ఀ) unsupported in many fonts |
| Font recommendation | Noto Sans Telugu; Tiro Telugu for advanced characters |
| Shared with Kannada | Alphasyllabary system, similar vowel sign placement |
| User base | Andhra Pradesh, Telangana -- large dairy farming population |

### 4.2 Tamil (ta-IN)

| Aspect | Details |
|--------|---------|
| Script | Tamil (U+0B80-U+0BFF), spare and rounded-but-angular |
| Rendering challenges | Fewer complex ligatures than other Dravidian scripts; Grantha Visarga only works with Noto Tamil fonts |
| Font recommendation | Noto Sans Tamil |
| Special consideration | Tamil script reform means fewer conjuncts -- actually simpler to render than Kannada |
| User base | Tamil Nadu -- active dairy cooperatives (Aavin), large livestock sector |

### 4.3 Hindi (hi-IN)

| Aspect | Details |
|--------|---------|
| Script | Devanagari (U+0900-U+097F) |
| Rendering challenges | Generally well-supported on all Android devices; conjunct rendering varies by font |
| Font recommendation | Noto Sans Devanagari (bundled on most Android devices) |
| Special consideration | Best STT/TTS support among all Indian languages |
| User base | Hindi belt states -- massive potential expansion |

### 4.4 Marathi (mr-IN)

| Aspect | Details |
|--------|---------|
| Script | Devanagari (same as Hindi) |
| Rendering challenges | Conjunct rendering differs between fonts (e.g., Mangal vs Arial Unicode MS); some Marathi-specific characters render differently than Hindi |
| Font recommendation | Same Noto Sans Devanagari, but test Marathi-specific conjuncts |
| Special consideration | Shares script with Hindi but has distinct vocabulary and grammar; must be a separate translation, not a Hindi variant |
| User base | Maharashtra -- large dairy state (Amul model) |

### 4.5 Malayalam (ml-IN)

| Aspect | Details |
|--------|---------|
| Script | Malayalam (U+0D00-U+0D7F), highly rounded and dense |
| Rendering challenges | Most visually complex of all Indian scripts; many stacked loops and connected forms; OpenType shaping requires strict feature execution order |
| Font recommendation | Noto Sans Malayalam; requires thorough testing |
| Special consideration | Complex script shaping is computationally heavier -- test rendering performance on budget devices |
| User base | Kerala -- advanced dairy cooperative system (Milma) |

### 4.6 Multi-Script Font Strategy

**Google Anek** font family addresses multi-script consistency:
- Covers: Bangla, Devanagari, Gujarati, Gurmukhi, Kannada, Latin, Malayalam, Odia, Tamil, Telugu
- All 10 scripts designed simultaneously for visual harmony
- 8 weights and 5 widths per script
- Available on Google Fonts

**Recommendation:** Use Noto Sans family for production (better per-script optimization). Consider Anek for marketing/landing pages where cross-script visual consistency matters.

---

## 5. Text-to-Speech for Farming Content

### 5.1 TTS Engines Supporting Natural Kannada

| Engine | Voices | Quality | Offline | API available | Best for |
|--------|--------|---------|---------|---------------|----------|
| **Sarvam Bulbul V3** | Multiple | Natural prosody | No | Yes | App integration |
| **Google Cloud TTS** | Standard + WaveNet | Good | No | Yes | General use |
| **Azure Neural TTS** | 6 kn-IN voices | Good, HD voices | No | Yes | Enterprise |
| **Bhashini TTS** | Multiple models | Varies | No | Yes (free) | Government alignment |
| **Narakeet** | 97 Kannada voices | Good | No | Yes | Pre-recorded content |
| **MicMonster** | HD voices | Emotion-aware | No | Yes | Advisory content |

### 5.2 Pre-Recorded vs. Dynamic TTS

| Approach | Pros | Cons | Best for |
|----------|------|------|----------|
| **Pre-recorded audio** | Highest quality; works offline; zero latency; local dialect accuracy | Expensive to produce; hard to update; storage-heavy | Core farming terms, common advisory phrases, onboarding instructions |
| **Dynamic TTS** | Scales to any content; easy to update; personalizable | Requires internet; variable quality; may mispronounce domain terms | Dynamic advisory content, scheme information, personalized reports |
| **Hybrid** | Best of both worlds | More complex to implement | PashuRaksha recommended approach |

**Hybrid strategy for PashuRaksha:**
1. **Pre-record** the top 50 farming advisory phrases (vaccination reminders, feed schedules, health alerts) in studio-quality Kannada
2. **Dynamic TTS** for personalized content (animal names, milk quantities, scheme details)
3. **Cache** TTS output for frequently accessed dynamic content

### 5.3 Audio Content Caching for Offline Use

```typescript
// Pattern: Cache TTS audio for offline playback
interface CachedAudio {
  key: string;        // hash of text + language
  filePath: string;   // local file system path
  textHash: string;   // detect content changes
  createdAt: number;  // cache expiry management
  language: string;   // kn, en, te, etc.
}

// Strategy:
// 1. Check local cache by text hash
// 2. If cached and not expired, play from local file
// 3. If not cached, call TTS API, save to FileSystem, play
// 4. Pre-cache critical advisory content on wifi
// 5. Evict least-recently-used when storage exceeds 50MB
```

**Offline priority content to pre-cache:**
- Health emergency instructions (10 phrases)
- Vaccination schedule reminders (20 phrases)
- Common symptom descriptions (15 phrases)
- Milk recording confirmation phrases (10 phrases)

---

## 6. Implementation Patterns

### 6.1 Translation Workflow

**Phase 1 -- Prototype (current sprint):**
```
Developer writes English strings
  -> Google Translate for initial Kannada draft
  -> Local Karnataka team member reviews + corrects
  -> Ship with reviewed translations
```

**Phase 2 -- Production:**
```
Product team writes English strings in i18next JSON
  -> Upload to Crowdin/Lokalise
  -> Professional translator (Kannada native, agricultural background)
  -> Reviewer (different translator) validates
  -> Export approved JSON to codebase via CI/CD
  -> Glossary of agricultural terms maintained separately
```

**Key roles:**
- **Agricultural domain translator:** Must understand ಪಶುಪಾಲನೆ (animal husbandry) terminology
- **Linguistic reviewer:** Native Kannada speaker from target district, different person from translator
- **Style guide owner:** Maintains tone (informal, supportive, non-technical) and glossary

### 6.2 Translation File Structure

```
/locales
  /en
    common.json          # Shared UI: buttons, nav, errors
    animals.json         # Animal management screens
    milk.json            # Milk recording screens
    health.json          # Health & vaccination
    schemes.json         # Government schemes
    advisory.json        # Farming advisory content
  /kn
    common.json
    animals.json
    milk.json
    health.json
    schemes.json
    advisory.json
```

Namespace-based loading ensures only relevant translations are loaded per screen, reducing memory on budget devices.

### 6.3 Crowdsourced Translation Patterns

For expansion beyond Kannada (Telugu, Tamil, Hindi, Marathi, Malayalam):

1. **Seed translations:** Use Bhashini MT API to generate initial machine translations from Kannada
2. **Community review:** Deploy a Crowdin project where local agricultural extension workers review and correct
3. **Quality gates:** Machine-translated strings marked as "unreviewed"; require 2 approvals before production
4. **Glossary enforcement:** Agricultural terms locked in glossary; translators must use approved terms
5. **Incentives:** Recognition in app credits, certificates (Crowdin Volunteer Certificates), early feature access

### 6.4 Fallback Strategy When Translation Is Missing

```typescript
// i18next fallback chain configuration
i18n.init({
  fallbackLng: {
    'kn': ['en'],       // Kannada -> English
    'te': ['kn', 'en'], // Telugu -> Kannada -> English
    'ta': ['en'],       // Tamil -> English
    'hi': ['en'],       // Hindi -> English
    'mr': ['hi', 'en'], // Marathi -> Hindi -> English
    'ml': ['en'],       // Malayalam -> English
    'default': ['en'],
  },
  // Show key name in development, fallback silently in production
  saveMissing: __DEV__,
  missingKeyHandler: (lngs, ns, key) => {
    if (__DEV__) console.warn(`Missing i18n: ${key} for ${lngs}`);
    // In production, log to analytics for translation gap tracking
  },
});
```

**Visual fallback pattern:**
1. Show translated text if available
2. Show English text if translation missing (with subtle indicator in dev)
3. Show translation key as last resort (never in production)

### 6.5 RTL/LTR Handling

All PashuRaksha target languages are LTR (left-to-right):
- Kannada, Telugu, Tamil, Hindi, Marathi, Malayalam: All LTR
- English: LTR
- Urdu (potential future): RTL

**No RTL handling needed for current scope.** If Urdu is added later, use `I18nManager.forceRTL()` from React Native and test all layouts.

### 6.6 Testing Multilingual Apps

| Test type | Tool/approach | Frequency |
|-----------|--------------|-----------|
| **Pseudo-localization** | i18next pseudo plugin (doubles text length, adds accents) | Every PR |
| **Visual regression** | Storybook + screenshots in each language | Weekly |
| **Real device testing** | 3 budget Android devices (Redmi, Realme, Samsung A-series) | Before release |
| **Content review** | Native speaker walkthrough of all screens | Before release |
| **Voice input testing** | Record 50 common phrases per dialect, measure WER | Monthly |
| **Offline testing** | Airplane mode: verify cached translations + audio work | Before release |

---

## 7. Government Language Requirements

### 7.1 Karnataka Official Language Act (1963) + Comprehensive Development Act (2022)

**Key provisions affecting PashuRaksha:**

| Requirement | Source | PashuRaksha implication |
|-------------|--------|------------------------|
| Kannada is the official language of Karnataka | Act 26 of 1963 | App MUST support Kannada as primary language |
| IT usage must include Kannada | Act 13 of 2023 | All digital interfaces must have Kannada option |
| Products sold in Karnataka must have Kannada labeling | 2022 Act | App store listing must be in Kannada |
| Government communications must be in Kannada | 2022 Act | Any government scheme information must be in Kannada |
| Enforcement authority with state/district/taluka committees | 2022 Act | Compliance may be audited |
| Non-compliance attracts penalties | 2022 Act | Must be taken seriously |

**Compliance checklist for PashuRaksha:**
- [x] Kannada as default/primary language option (already in spec)
- [ ] All government scheme information in Kannada
- [ ] App store listing (Google Play) in Kannada
- [ ] Kannada nameplate/branding in app
- [ ] Unicode font support for Kannada text input
- [ ] Kannada voice input option (specified in mobile-voice spec)

### 7.2 Central Government -- Official Languages Act

The Official Languages Act, 1963 (amended 1967) designates Hindi and English as official languages of the Union. For apps interfacing with central government schemes (PM Kisan, NDDB programs):
- Hindi and English support adds compliance value
- Bilingual (Hindi + English) display may be required for central scheme content

### 7.3 Accessibility Mandates

The Rights of Persons with Disabilities Act, 2016 requires:
- Screen reader compatibility (TalkBack on Android)
- Sufficient color contrast
- Touch target sizes >= 48dp
- Voice-based interaction alternatives (already in PashuRaksha spec)

These align with PashuRaksha's voice-first approach and large-icon design for rural users.

---

## 8. PashuRaksha-Specific Recommendations

### 8.1 Phase 1 -- Sprint Prototype (Now)

| Item | Recommendation | Priority |
|------|---------------|----------|
| i18n setup | i18next + expo-localization + 2 languages (kn, en) | P0 |
| Translation files | Namespace per feature; manual Kannada translations | P0 |
| Font strategy | System fonts + bundled Noto Sans Kannada Regular as fallback | P1 |
| Number format | Always Latin digits, ₹ for currency | P0 |
| Voice input | Sarvam AI Saaras V3 for milk recording (already specified) | P0 |
| Language picker | Simple toggle on settings screen (Kannada / English) | P1 |
| Text expansion | Test all screens with real Kannada text; no fixed-width buttons | P1 |

### 8.2 Phase 2 -- Production

| Item | Recommendation | Priority |
|------|---------------|----------|
| Translation platform | Crowdin or Lokalise with agricultural glossary | P1 |
| TTS integration | Sarvam Bulbul V3 for dynamic + pre-recorded audio for core phrases | P1 |
| Bhashini integration | Machine translation API for admin dashboard content | P2 |
| Offline audio cache | Pre-cache health alerts and advisory content on WiFi | P1 |
| Code-switching | Evaluate Sarvam/Reverie for advisory chat feature | P2 |
| Expansion languages | Add Telugu and Hindi first (largest dairy farming populations) | P2 |

### 8.3 Phase 3 -- Scale

| Item | Recommendation | Priority |
|------|---------------|----------|
| All 6 languages | kn, en, te, ta, hi, mr, ml | P1 |
| Crowdsourced translation | Agricultural extension workers as community translators | P2 |
| Dialect handling | Collect field audio from 5 Karnataka districts; fine-tune STT | P2 |
| Full voice assistant | Voice-driven navigation for illiterate users | P1 |
| Regional TTS voices | Different voice per language with natural prosody | P2 |

### 8.4 Voice Provider Strategy

```
Primary STT:   Sarvam AI Saaras V3 (best rural Indian accuracy)
Fallback STT:  Bhashini ASR (free, government-aligned)
Primary TTS:   Sarvam AI Bulbul V3 (natural Indian voice)
Fallback TTS:  Google Cloud TTS (broader language coverage)
Translation:   Bhashini MT API (free, all 22 languages)
```

### 8.5 Budget Device Performance Targets

| Metric | Target | How to achieve |
|--------|--------|----------------|
| First Meaningful Paint | < 3 seconds | Lazy-load translation namespaces |
| Language switch | < 500ms | Preload both kn + en on startup |
| Voice recording start | < 1 second | Pre-initialize audio capture |
| STT response | < 3 seconds | Use streaming API if available |
| TTS playback start | < 2 seconds | Cache frequently used audio |
| Translation file size | < 50KB per language | Namespace splitting |

---

## Sources

### Kannada & Script Rendering
- [Noto Sans Kannada - Google Fonts](https://fonts.google.com/noto/specimen/Noto+Sans+Kannada)
- [Noto Sans Kannada Guide - FontForge](https://fontforge.io/noto-sans-kannada/)
- [ScriptSource - Kannada Unicode Status](https://scriptsource.org/cms/scripts/page.php?item_id=entry_detail&uid=ur8y3qj6yk)
- [Google Anek Multi-Script Font](https://design.google/library/anek-multiscript)
- [OpenType for Malayalam - Microsoft](https://learn.microsoft.com/en-us/typography/script-development/malayalam)
- [Text Expansion in Translation - W3C](https://www.w3.org/International/articles/article-text-size)

### Voice & Speech
- [Sarvam AI Speech-to-Text API](https://www.sarvam.ai/apis/speech-to-text)
- [Sarvam Saaras V3 ASR](https://www.sarvam.ai/blogs/asr)
- [Sarvam Bulbul-v2 Breakthrough](https://www.gptfrontier.com/sarvam-ais-bulbul-v2-indias-multilingual-voice-tech-breakthrough/)
- [Sarvam AI Models](https://www.sarvam.ai/models)
- [Bhashini APIs Documentation](https://bhashini.gitbook.io/bhashini-apis)
- [Bhashini Platform](https://www.bhashini.ai/)
- [BHASHINI Bridging 1.4 Billion Citizens](https://egov.eletsonline.com/2026/03/bhashini-bridging-1-4-billion-citizens-to-services-and-opportunities-via-language-ai/)
- [Google Cloud Speech-to-Text Languages](https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages)
- [Azure Speech Language Support](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support)
- [Azure Feb 2025 HD Voices Update](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/azure-ai-speech-text-to-speech-feb-2025-updates-new-hd-voices-and-more/4387263)
- [Code-Switching ASR for Indic Languages](https://ieeexplore.ieee.org/iel8/6287639/10820123/10835062.pdf)
- [Reverie Code-Mixing in STT](https://reverieinc.com/blog/code-mixing-and-switching-feature-in-speech-to-text/)
- [Soniox Kannada STT](https://soniox.com/speech-to-text/kannada)

### i18n Implementation
- [Expo Localization Docs](https://docs.expo.dev/versions/latest/sdk/localization/)
- [i18n in React Native with Expo](https://dev.to/lucasferreiralimax/i18n-in-react-native-with-expo-2j0j)
- [Multi-Language React Native 2025](https://medium.com/@devanshtiwari365/how-to-build-a-multi-language-app-with-i18n-in-react-native-2025-edition-24318950dd8c)
- [React Native Multilingual Indian Languages](https://medium.com/@bhuvin25/making-your-react-native-app-multilingual-supporting-indian-and-foreign-languages-748405c31ed9)
- [Android Multi-Language Support](https://developer.android.com/training/basics/supporting-devices/languages)

### Indian App Patterns
- [Multilingual App Design for India - Devexis](https://devexis.com/designing-a-multilingual-mobile-app-for-indias-diverse-market-ux-technical-tips/)
- [Localizing Apps for India - AppTweak](https://www.apptweak.com/en/aso-blog/how-to-localize-your-app-in-india)
- [PhonePe Indus Appstore](https://www.phonepe.com/press/phonepe-announces-the-launch-of-the-indus-appstore-developer-platform/)
- [Multilingual WhatsApp Bots India - Sinch](https://sinch.com/blog/multilingual-whatsapp-bots-india/)

### Translation Workflow
- [Crowdin Crowdsourcing](https://support.crowdin.com/enterprise/crowdsourcing/)
- [Crowdsourcing 101 - Transifex](https://www.transifex.com/blog/2016/crowdsourcing-101)
- [Collaborative Translation Workflow - ACM](https://dl.acm.org/doi/10.1145/2145204.2145382)

### Kannada Vocabulary
- [Agriculture Vocabulary in Kannada - LearnEntry](https://www.learnentry.com/english-kannada/vocabulary/agriculture-in-kannada/)
- [Farm Animals in Kannada - Talkpal](https://talkpal.ai/vocabulary/farm-animals-and-pets-vocabulary-in-kannada/)
- [Kannada Agriculture Dictionary - Shabdkosh](https://www.shabdkosh.com/dictionary/english-kannada/agriculture/agriculture-meaning-in-kannada)

### Government Compliance
- [Kannada Language Comprehensive Development Act 2022](https://prsindia.org/bills/states/the-kannada-language-comprehensive-development-bill-2022)
- [Karnataka Official Language Act 1963](https://www.indiacode.nic.in/handle/123456789/7524?view_type=browse)
- [Karnataka Mandates Kannada for Government Communications](https://thelogicalindian.com/karnataka-mandates-kannada-for-all-government-communications-warns-of-disciplinary-action-for-non-compliance/)
- [Sarvam AI India AI Impact Summit 2026](https://www.medianama.com/2026/02/223-sarvam-ai-india-ai-impact-summit-2026/)
