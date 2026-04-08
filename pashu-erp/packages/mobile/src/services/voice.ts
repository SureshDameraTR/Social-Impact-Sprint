/**
 * Voice recording + STT service
 * Uses Sarvam AI Saaras V3 for Kannada speech-to-text
 * Falls back to mock in development (work laptop constraint)
 */

import { parseKannadaNumber } from './kannada-parser';

export type VoiceContext = 'milk_quantity' | 'sell_quantity' | 'generic';

export interface VoiceResult {
  text: string;
  confidence: number;
  parsedNumber: number | null;
  language: string;
}

const SARVAM_API_URL = 'https://api.sarvam.ai/speech-to-text';

// Mock STT responses for demo (no actual API call needed on work laptop)
const MOCK_RESPONSES: Record<VoiceContext, VoiceResult> = {
  milk_quantity: { text: '\u0C90\u0CA6\u0CC1 \u0CB2\u0CC0\u0C9F\u0CB0\u0CCD', confidence: 0.92, parsedNumber: 5, language: 'kn' },
  sell_quantity: { text: '\u0CB9\u0CA4\u0CCD\u0CA4\u0CC1 \u0CAE\u0CCA\u0C9F\u0CCD\u0C9F\u0CC6', confidence: 0.88, parsedNumber: 10, language: 'kn' },
  generic: { text: '\u0CAE\u0CC2\u0CB0\u0CC1', confidence: 0.85, parsedNumber: 3, language: 'kn' },
};

const USE_MOCK = process.env.EXPO_PUBLIC_SARVAM_API_KEY == null;

/**
 * Transcribe audio to text using Sarvam AI Saaras V3.
 * In demo/dev mode (no API key), returns mock responses after a realistic delay.
 */
export async function transcribeAudio(
  audioUri: string,
  context: VoiceContext = 'generic'
): Promise<VoiceResult> {
  if (USE_MOCK) {
    // Simulate network + processing delay for realistic demo
    await new Promise(resolve => setTimeout(resolve, 1500));
    return MOCK_RESPONSES[context];
  }

  // Production path: call Sarvam AI API
  const formData = new FormData();
  formData.append('file', {
    uri: audioUri,
    type: 'audio/wav',
    name: 'recording.wav',
  } as unknown as Blob);
  formData.append('language_code', 'kn');
  formData.append('model', 'saaras:v3');

  const response = await fetch(SARVAM_API_URL, {
    method: 'POST',
    headers: {
      'api-subscription-key': process.env.EXPO_PUBLIC_SARVAM_API_KEY!,
    },
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Sarvam API ${response.status}: ${await response.text()}`);
  }

  const data = await response.json();
  const text: string = data.transcript || '';
  const parsedNumber = parseKannadaNumber(text);

  return {
    text,
    confidence: data.confidence ?? 0.8,
    parsedNumber,
    language: data.language_code || 'kn',
  };
}
