import React, { useEffect, useState, useCallback, useRef } from 'react';
import { AppState, AppStateStatus } from 'react-native';
import {
  QueryClient,
  QueryClientProvider,
  onlineManager,
  focusManager,
} from '@tanstack/react-query';
import NetInfo from '@react-native-community/netinfo';
import { sync, getAll, type QueuedMutation } from '../services/offline-queue';
import * as Storage from '../config/storage';
import { OfflineBanner } from '../components/OfflineBanner';

// Create a stable QueryClient instance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Keep data fresh for 5 minutes before refetching
      staleTime: 5 * 60 * 1000,
      // Cache data for 30 minutes
      gcTime: 30 * 60 * 1000,
      // Retry once on failure (rural 2G/3G connections)
      retry: 1,
      retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 10000),
    },
    mutations: {
      retry: 0,
    },
  },
});

/**
 * Replays a single queued mutation against the API.
 * This function is passed to sync() to avoid circular dependency with api.ts.
 */
async function replayMutation(mutation: QueuedMutation): Promise<boolean> {
  const API_URL = process.env.EXPO_PUBLIC_API_URL;
  if (!API_URL) return false;

  const token = await Storage.getItemAsync('auth_token');
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };

  try {
    const res = await fetch(`${API_URL}${mutation.url}`, {
      method: mutation.method,
      headers,
      ...(mutation.body ? { body: JSON.stringify(mutation.body) } : {}),
    });

    // 2xx = success, 4xx = client error (don't retry), 5xx = server error (keep in queue)
    if (res.ok) return true;
    if (res.status >= 400 && res.status < 500) {
      // Client errors won't succeed on retry — remove from queue
      console.warn(
        `Offline queue: dropping mutation ${mutation.id} (${mutation.method} ${mutation.url}) — server returned ${res.status}`
      );
      return true;
    }
    return false;
  } catch {
    return false;
  }
}

interface QueryProviderProps {
  children: React.ReactNode;
}

export function QueryProvider({ children }: QueryProviderProps) {
  const [syncingCount, setSyncingCount] = useState(0);
  const [syncComplete, setSyncComplete] = useState(false);
  const isSyncing = useRef(false);

  // Wire NetInfo into React Query's onlineManager
  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener((state) => {
      const connected = state.isConnected ?? false;
      onlineManager.setOnline(connected);
    });
    return () => unsubscribe();
  }, []);

  // Wire AppState into React Query's focusManager
  useEffect(() => {
    const subscription = AppState.addEventListener(
      'change',
      (status: AppStateStatus) => {
        focusManager.setFocused(status === 'active');
      }
    );
    return () => subscription.remove();
  }, []);

  // Sync queued mutations when we come back online
  const performSync = useCallback(async () => {
    if (isSyncing.current) return;

    const pending = await getAll();
    if (pending.length === 0) return;

    isSyncing.current = true;
    setSyncingCount(pending.length);
    setSyncComplete(false);

    try {
      const result = await sync(replayMutation);
      if (result.succeeded > 0) {
        setSyncComplete(true);
        // Invalidate all queries so screens refetch fresh data
        queryClient.invalidateQueries();
      }
    } finally {
      setSyncingCount(0);
      isSyncing.current = false;
    }
  }, []);

  // Listen for online status changes to trigger sync
  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener((state) => {
      if (state.isConnected) {
        performSync();
      }
    });
    return () => unsubscribe();
  }, [performSync]);

  // Also sync when app comes to foreground
  useEffect(() => {
    const subscription = AppState.addEventListener(
      'change',
      (status: AppStateStatus) => {
        if (status === 'active') {
          performSync();
        }
      }
    );
    return () => subscription.remove();
  }, [performSync]);

  // Clear syncComplete flag after banner auto-hides
  useEffect(() => {
    if (syncComplete) {
      const timer = setTimeout(() => setSyncComplete(false), 4000);
      return () => clearTimeout(timer);
    }
  }, [syncComplete]);

  return (
    <QueryClientProvider client={queryClient}>
      <OfflineBanner
        syncingCount={syncingCount}
        syncComplete={syncComplete}
      />
      {children}
    </QueryClientProvider>
  );
}
