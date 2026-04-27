/**
 * Voice recording + STT service
 * Uses backend proxy to Sarvam AI Saaras V3 for Kannada speech-to-text.
 * The backend at /v1/voice/stt and /v1/voice/tts should proxy requests
 * to Sarvam AI with the API key stored server-side.
 */

import { parseKannadaNumber } from './kannada-parser';

export type VoiceContext = 'milk_quantity' | 'sell_quantity' | 'generic';

export interface VoiceResult {
  text: string;
  confidence: number;
  parsedNumber: number | null;
  language: string;
}

const API_URL = process.env.EXPO_PUBLIC_API_URL;

/** Mock responses keyed by context, used when no real backend is available */
const MOCK_RESPONSES: Record<VoiceContext, VoiceResult> = {
  milk_quantity: { text: '\u0CAE\u0CC2\u0CB0\u0CC1 \u0CB2\u0CC0\u0C9F\u0CB0\u0CCD', confidence: 0.95, parsedNumber: 3, language: 'kn' },
  sell_quantity: { text: '\u0C90\u0CA6\u0CC1', confidence: 0.92, parsedNumber: 5, language: 'kn' },
  generic: { text: '\u0CB9\u0CA4\u0CCD\u0CA4\u0CC1', confidence: 0.90, parsedNumber: 10, language: 'kn' },
};

/**
 * Transcribe audio to text via backend proxy to Sarvam AI.
 * If the URI starts with "mock://", returns a mock response for dev/testing.
 */
export async function transcribeAudio(
  audioUri: string,
  context: VoiceContext = 'generic'
): Promise<VoiceResult> {
  // Mock path for dev/testing (no real mic available)
  if (audioUri.startsWith('mock://')) {
    await new Promise(resolve => setTimeout(resolve, 500));
    return MOCK_RESPONSES[context];
  }

  // Proxy through our backend (which holds the Sarvam API key)
  const formData = new FormData();
  formData.append('file', {
    uri: audioUri,
    type: 'audio/wav',
    name: 'recording.wav',
  } as unknown as Blob);
  formData.append('language_code', 'kn');
  formData.append('model', 'saaras:v3');

  const response = await fetch(`${API_URL}/voice/stt`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Voice STT API ${response.status}: ${await response.text()}`);
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
