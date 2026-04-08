import React from 'react';
import { Stack } from 'expo-router';
import { PaperProvider } from 'react-native-paper';
import { theme } from '../src/config/theme';
import '../src/i18n';

export default function RootLayout() {
  return (
    <PaperProvider theme={theme}>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(auth)" />
        <Stack.Screen name="(tabs)" />
        <Stack.Screen
          name="animal/[id]"
          options={{ headerShown: true, title: '' }}
        />
        <Stack.Screen
          name="animal/add"
          options={{ headerShown: true, title: '' }}
        />
        <Stack.Screen
          name="milk/history"
          options={{ headerShown: true, title: '' }}
        />
        <Stack.Screen
          name="smart-farm"
          options={{ headerShown: true, title: '' }}
        />
        <Stack.Screen
          name="profile"
          options={{ headerShown: true, title: '' }}
        />
      </Stack>
    </PaperProvider>
  );
}
