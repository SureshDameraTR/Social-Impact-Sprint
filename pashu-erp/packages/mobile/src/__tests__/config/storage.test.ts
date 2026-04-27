/**
 * Storage wrapper tests.
 *
 * The storage module provides a platform-adaptive wrapper:
 * - On native: delegates to expo-secure-store
 * - On web: delegates to sessionStorage
 *
 * In the Jest/jsdom environment, Platform.OS = 'web',
 * so we test the web path (sessionStorage) and verify the async API contract.
 */

// We do NOT mock storage here — we want to test the real module.
// But we need to mock expo-secure-store to prevent import errors on non-native.
jest.mock('expo-secure-store', () => ({
  getItemAsync: jest.fn(),
  setItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}));

describe('Storage wrapper', () => {
  const storageBackup: Record<string, string> = {};

  beforeEach(() => {
    // Reset sessionStorage for each test
    if (typeof sessionStorage !== 'undefined') {
      sessionStorage.clear();
    }

    // Provide a minimal sessionStorage if running in a non-browser env
    if (typeof globalThis.sessionStorage === 'undefined') {
      Object.defineProperty(globalThis, 'sessionStorage', {
        value: {
          _store: {} as Record<string, string>,
          getItem(key: string) { return this._store[key] ?? null; },
          setItem(key: string, val: string) { this._store[key] = val; },
          removeItem(key: string) { delete this._store[key]; },
          clear() { this._store = {}; },
        },
        writable: true,
        configurable: true,
      });
    }

    // Clear require cache so storage module re-evaluates Platform check
    jest.resetModules();
  });

  it('exports getItemAsync, setItemAsync, deleteItemAsync', () => {
    const Storage = require('../../config/storage');
    expect(typeof Storage.getItemAsync).toBe('function');
    expect(typeof Storage.setItemAsync).toBe('function');
    expect(typeof Storage.deleteItemAsync).toBe('function');
  });

  it('getItemAsync returns a Promise', () => {
    const Storage = require('../../config/storage');
    const result = Storage.getItemAsync('any-key');
    expect(result).toBeInstanceOf(Promise);
  });

  it('setItemAsync returns a Promise', () => {
    const Storage = require('../../config/storage');
    const result = Storage.setItemAsync('key', 'value');
    expect(result).toBeInstanceOf(Promise);
  });

  it('deleteItemAsync returns a Promise', () => {
    const Storage = require('../../config/storage');
    const result = Storage.deleteItemAsync('key');
    expect(result).toBeInstanceOf(Promise);
  });

  it('getItemAsync returns null for non-existent key on web', async () => {
    const Storage = require('../../config/storage');
    const value = await Storage.getItemAsync('nonexistent');
    expect(value).toBeNull();
  });

  it('setItemAsync + getItemAsync round-trips on web', async () => {
    const Storage = require('../../config/storage');
    await Storage.setItemAsync('auth_token', 'jwt-abc-123');
    const value = await Storage.getItemAsync('auth_token');
    expect(value).toBe('jwt-abc-123');
  });

  it('deleteItemAsync removes a value on web', async () => {
    const Storage = require('../../config/storage');
    await Storage.setItemAsync('auth_token', 'jwt-abc-123');
    await Storage.deleteItemAsync('auth_token');
    const value = await Storage.getItemAsync('auth_token');
    expect(value).toBeNull();
  });
});
