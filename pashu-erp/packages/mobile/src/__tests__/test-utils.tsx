/**
 * Shared test utilities for PashuRaksha mobile tests.
 *
 * Provides the PaperProvider wrapper needed by all screen/component tests.
 * Individual test files should call jest.mock() for their specific needs.
 */
import React from 'react';
import { PaperProvider } from 'react-native-paper';
import { theme } from '../config/theme';

/**
 * Wraps a component in PaperProvider with the app theme.
 * Usage: render(wrap(<MyComponent />))
 */
export function wrap(ui: React.ReactElement) {
  return <PaperProvider theme={theme}>{ui}</PaperProvider>;
}
