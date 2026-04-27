import { router } from 'expo-router';
import NetInfo from '@react-native-community/netinfo';
import * as Storage from './storage';
import { enqueue } from '../services/offline-queue';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL;
if (!API_BASE_URL) {
  throw new Error('EXPO_PUBLIC_API_URL environment variable is required');
}

const REQUEST_TIMEOUT_MS = 15_000;
const MAX_RETRIES = 3;
const BACKOFF_BASE_MS = 1000;

/** Methods that mutate data and can be queued offline */
const MUTABLE_METHODS = new Set(['POST', 'PATCH', 'DELETE']);

/**
 * Check whether the device currently has an internet connection.
 * Returns false when NetInfo reports no connectivity, true otherwise.
 */
async function isOnline(): Promise<boolean> {
  try {
    const state = await NetInfo.fetch();
    return state.isConnected ?? false;
  } catch {
    // If NetInfo itself fails, assume online and let fetch decide
    return true;
  }
}

/**
 * Determine whether a caught error is a network-level failure
 * (as opposed to an HTTP error from the server).
 */
function isNetworkError(error: unknown): boolean {
  if (error instanceof TypeError && error.message === 'Network request failed') {
    return true;
  }
  if (error instanceof DOMException && error.name === 'AbortError') {
    return true;
  }
  return false;
}

/**
 * Marker interface for responses that were queued offline
 * rather than returned by the server.
 */
export interface QueuedResponse {
  _queued: true;
  _queuedId: string;
}

// Global snackbar callback — set by the root layout so the ApiClient
// can show toasts without importing React hooks.
let _showOfflineToast: ((message: string) => void) | null = null;

export function setOfflineToastCallback(cb: (message: string) => void): void {
  _showOfflineToast = cb;
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async handleUnauthorized(): Promise<never> {
    await Storage.deleteItemAsync('auth_token');
    router.replace('/(auth)/login');
    throw new Error('Session expired');
  }

  private async getHeaders(): Promise<HeadersInit> {
    const token = await Storage.getItemAsync('auth_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  }

  private async fetchWithTimeout(
    url: string,
    options: RequestInit
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
      const res = await fetch(url, { ...options, signal: controller.signal });
      return res;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  private async fetchWithRetry(
    url: string,
    options: RequestInit,
    retries: number = MAX_RETRIES
  ): Promise<Response> {
    for (let attempt = 0; attempt < retries; attempt++) {
      try {
        const res = await this.fetchWithTimeout(url, options);
        if (res.ok || res.status === 401 || attempt === retries - 1) return res;
        // Only retry on server errors (5xx)
        if (res.status < 500) return res;
      } catch (error) {
        if (attempt === retries - 1) throw error;
      }
      // Exponential backoff: 1s, 2s, 4s
      await new Promise((resolve) =>
        setTimeout(resolve, BACKOFF_BASE_MS * Math.pow(2, attempt))
      );
    }
    // Unreachable, but satisfies TypeScript
    throw new Error('Max retries exceeded');
  }

  /**
   * Try to queue a mutation offline when network is unavailable.
   * Returns a synthetic QueuedResponse if queued, or null if queueing
   * is not applicable (e.g. GET requests).
   */
  private async tryQueueOffline(
    method: string,
    path: string,
    body?: unknown
  ): Promise<QueuedResponse | null> {
    if (!MUTABLE_METHODS.has(method)) return null;

    const entry = await enqueue({
      method: method as 'POST' | 'PATCH' | 'DELETE',
      url: path,
      body,
    });

    if (_showOfflineToast) {
      _showOfflineToast('Saved offline — will sync when connected');
    }

    return { _queued: true, _queuedId: entry.id };
  }

  async get<T>(path: string): Promise<T> {
    const res = await this.fetchWithRetry(`${this.baseUrl}${path}`, {
      headers: await this.getHeaders(),
    });
    if (res.status === 401) await this.handleUnauthorized();
    if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
    return res.json();
  }

  async post<T>(path: string, body: unknown): Promise<T | QueuedResponse> {
    // Pre-check connectivity for fast offline path
    const online = await isOnline();
    if (!online) {
      const queued = await this.tryQueueOffline('POST', path, body);
      if (queued) return queued as T | QueuedResponse;
    }

    try {
      const res = await this.fetchWithRetry(`${this.baseUrl}${path}`, {
        method: 'POST',
        headers: await this.getHeaders(),
        body: JSON.stringify(body),
      });
      if (res.status === 401) await this.handleUnauthorized();
      if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
      return res.json();
    } catch (error) {
      // Network failure after retries exhausted — queue it
      if (isNetworkError(error)) {
        const queued = await this.tryQueueOffline('POST', path, body);
        if (queued) return queued as T | QueuedResponse;
      }
      throw error;
    }
  }

  async patch<T>(path: string, body: unknown): Promise<T | QueuedResponse> {
    const online = await isOnline();
    if (!online) {
      const queued = await this.tryQueueOffline('PATCH', path, body);
      if (queued) return queued as T | QueuedResponse;
    }

    try {
      const res = await this.fetchWithRetry(`${this.baseUrl}${path}`, {
        method: 'PATCH',
        headers: await this.getHeaders(),
        body: JSON.stringify(body),
      });
      if (res.status === 401) await this.handleUnauthorized();
      if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
      return res.json();
    } catch (error) {
      if (isNetworkError(error)) {
        const queued = await this.tryQueueOffline('PATCH', path, body);
        if (queued) return queued as T | QueuedResponse;
      }
      throw error;
    }
  }

  async delete(path: string): Promise<void | QueuedResponse> {
    const online = await isOnline();
    if (!online) {
      const queued = await this.tryQueueOffline('DELETE', path);
      if (queued) return queued;
    }

    try {
      const res = await this.fetchWithRetry(`${this.baseUrl}${path}`, {
        method: 'DELETE',
        headers: await this.getHeaders(),
      });
      if (res.status === 401) await this.handleUnauthorized();
      if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
    } catch (error) {
      if (isNetworkError(error)) {
        const queued = await this.tryQueueOffline('DELETE', path);
        if (queued) return queued;
      }
      throw error;
    }
  }

  async upload<T>(path: string, formData: FormData): Promise<T> {
    // Uploads are not queued — binary data in AsyncStorage is impractical
    const token = await Storage.getItemAsync('auth_token');
    const res = await this.fetchWithTimeout(`${this.baseUrl}${path}`, {
      method: 'POST',
      body: formData,
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });
    if (res.status === 401) await this.handleUnauthorized();
    if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
    return res.json();
  }
}

export const api = new ApiClient(API_BASE_URL);
