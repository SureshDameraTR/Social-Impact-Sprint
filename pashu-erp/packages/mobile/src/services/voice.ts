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

/**
 * Transcribe audio to text via backend proxy to Sarvam AI.
 */
export async function transcribeAudio(
  audioUri: string,
  context: VoiceContext = 'generic'
): Promise<VoiceResult> {
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
