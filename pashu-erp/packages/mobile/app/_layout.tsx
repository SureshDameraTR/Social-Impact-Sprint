import { enableFreeze } from 'react-native-screens';
// Freeze inactive screens to reduce JS re-renders on low-end devices.
// Native screens are enabled by default in react-native-screens v4+.
enableFreeze(true);

import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator, StyleSheet, Text as RNText, Pressable } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Stack, Redirect } from 'expo-router';
import { PaperProvider } from 'react-native-paper';
import * as Storage from '../src/config/storage';
import { useTranslation } from 'react-i18next';
import { theme, colors } from '../src/config/theme';
import { SnackbarProvider, useSnackbar } from '../src/hooks/useSnackbar';
import { useAppUpdate } from '../src/hooks/useAppUpdate';
import { QueryProvider } from '../src/providers/QueryProvider';
import { setOfflineToastCallback } from '../src/config/api';
import '../src/i18n';

// Inner component to use hooks inside the error boundary
function ErrorFallback({ onReload }: { onReload: () => void }) {
  const { t } = useTranslation();
  return (
    <View style={errorStyles.container}>
      <RNText style={errorStyles.emoji}>{'⚠️'}</RNText>
      <RNText style={errorStyles.title}>{t('error.title')}</RNText>
      <RNText style={errorStyles.subtitle}>{t('error.message')}</RNText>
      <Pressable style={errorStyles.button} onPress={onReload}>
        <RNText style={errorStyles.buttonText}>{t('error.reload')}</RNText>
      </Pressable>
    </View>
  );
}

// Error boundary to catch render crashes
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <ErrorFallback onReload={() => this.setState({ hasError: false })} />
      );
    }
    return this.props.children;
  }
}

const errorStyles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.surface,
    padding: 32,
  },
  emoji: { fontSize: 64, marginBottom: 16 },
  title: { fontSize: 24, fontWeight: '700', color: colors.onSurface, marginBottom: 8 },
  subtitle: { fontSize: 16, color: colors.onSurfaceVariant, textAlign: 'center', marginBottom: 24 },
  button: {
    backgroundColor: colors.primary,
    paddingHorizontal: 32,
    paddingVertical: 14,
    borderRadius: 16,
  },
  buttonText: { color: colors.onPrimary, fontSize: 18, fontWeight: '700' },
});

/**
 * Inner wrapper that wires the snackbar toast into the ApiClient
 * so offline queue operations can show "Saved offline" notifications.
 * Must be rendered inside SnackbarProvider.
 */
function OfflineToastWire({ children }: { children: React.ReactNode }) {
  const { showInfo } = useSnackbar();
  const { t } = useTranslation();

  useEffect(() => {
    setOfflineToastCallback(() => {
      showInfo(t('common.savedOffline'));
    });
    return () => setOfflineToastCallback(() => {});
  }, [showInfo, t]);

  return <>{children}</>;
}

export default function RootLayout() {
  const [authState, setAuthState] = useState<'loading' | 'authenticated' | 'unauthenticated'>('loading');
  useAppUpdate();

  useEffect(() => {
    (async () => {
      try {
        const token = await Storage.getItemAsync('auth_token');
        if (!token) {
          setAuthState('unauthenticated');
          return;
        }
        const API_URL = process.env.EXPO_PUBLIC_API_URL;
        const res = await fetch(`${API_URL}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          setAuthState('authenticated');
        } else {
          await Storage.deleteItemAsync('auth_token');
          setAuthState('unauthenticated');
        }
      } catch {
        setAuthState('unauthenticated');
      }
    })();
  }, []);

  if (authState === 'loading') {
    return (
      <View style={splashStyles.container}>
        <RNText style={splashStyles.emoji}>{'\uD83D\uDC04'}</RNText>
        <RNText style={splashStyles.title}>PashuRaksha</RNText>
        <ActivityIndicator size="large" color={colors.primary} style={splashStyles.spinner} />
      </View>
    );
  }

  if (authState === 'unauthenticated') {
    return (
      <SafeAreaProvider>
        <ErrorBoundary>
          <PaperProvider theme={theme}>
            <SnackbarProvider>
              <Stack screenOptions={{ headerShown: false }}>
                <Stack.Screen name="(auth)" />
              </Stack>
            </SnackbarProvider>
          </PaperProvider>
        </ErrorBoundary>
      </SafeAreaProvider>
    );
  }

  return (
    <SafeAreaProvider>
      <ErrorBoundary>
        <PaperProvider theme={theme}>
          <SnackbarProvider>
            <OfflineToastWire>
              <QueryProvider>
                <Stack screenOptions={{ headerShown: false }}>
                  <Stack.Screen name="(tabs)" />
                  <Stack.Screen
                    name="animal/[id]"
                    options={{ headerShown: true, title: 'Animal Details' }}
                  />
                  <Stack.Screen
                    name="animal/add"
                    options={{ headerShown: true, title: 'Add Animal' }}
                  />
                  <Stack.Screen
                    name="milk/history"
                    options={{ headerShown: true, title: 'Milk History' }}
                  />
                  <Stack.Screen
                    name="smart-farm"
                    options={{ headerShown: true, title: 'Smart Farm' }}
                  />
                  <Stack.Screen
                    name="profile"
                    options={{ headerShown: true, title: 'Profile' }}
                  />
                  <Stack.Screen
                    name="vet-photo"
                    options={{ headerShown: true, title: 'Send Photo to Vet' }}
                  />
                  <Stack.Screen
                    name="my-consultations"
                    options={{ headerShown: true, title: 'My Consultations' }}
                  />
                  <Stack.Screen
                    name="weather"
                    options={{ headerShown: true, title: 'Weather' }}
                  />
                  <Stack.Screen
                    name="vaccinations"
                    options={{ headerShown: true, title: 'Vaccinations' }}
                  />
                  <Stack.Screen
                    name="feed-calculator"
                    options={{ headerShown: true, title: 'Feed Calculator' }}
                  />
                  <Stack.Screen
                    name="insurance"
                    options={{ headerShown: true, title: 'Insurance' }}
                  />
                  <Stack.Screen
                    name="advisory"
                    options={{ headerShown: true, title: 'Advisory' }}
                  />
                  <Stack.Screen
                    name="community-alerts"
                    options={{ headerShown: true, title: 'Community Alerts' }}
                  />
                  <Stack.Screen
                    name="ethno-vet"
                    options={{ headerShown: true, title: 'Traditional Remedies' }}
                  />
                  <Stack.Screen
                    name="medicine-log"
                    options={{ headerShown: true, title: 'Medicine Log' }}
                  />
                  <Stack.Screen
                    name="pashu-aadhaar"
                    options={{ headerShown: true, title: 'Pashu Aadhaar' }}
                  />
                </Stack>
              </QueryProvider>
            </OfflineToastWire>
          </SnackbarProvider>
        </PaperProvider>
      </ErrorBoundary>
    </SafeAreaProvider>
  );
}

const splashStyles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.primary,
  },
  emoji: { fontSize: 72, marginBottom: 8 },
  title: { fontSize: 32, fontWeight: '700', color: colors.onPrimary, marginBottom: 24 },
  spinner: { marginTop: 16 },
});
