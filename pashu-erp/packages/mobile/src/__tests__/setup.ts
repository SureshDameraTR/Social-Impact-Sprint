/**
 * Jest setup file for the PashuRaksha mobile app.
 *
 * This runs via `setupFiles` before the test framework.
 * Only put environment-level setup here (env vars, global polyfills).
 * Do NOT use jest.mock() here — it is not available yet at this stage.
 */

// EXPO_PUBLIC env var needed by api.ts module-level check
process.env.EXPO_PUBLIC_API_URL = 'http://localhost:8000/v1';

// Suppress noisy RN warnings in test output
const originalWarn = console.warn;
console.warn = (...args: unknown[]) => {
  const msg = typeof args[0] === 'string' ? args[0] : '';
  if (
    msg.includes('Animated: `useNativeDriver`') ||
    msg.includes('componentWillReceiveProps') ||
    msg.includes('componentWillMount')
  ) {
    return;
  }
  originalWarn(...args);
};
