/**
 * Integration test: Milk Recording Flow
 * Covers the most common farmer action: log morning/evening milk for an animal.
 *
 * Flow: Select session → pick animal → enter quantity → Record → see confirmation
 */
import React from 'react';
import { render, fireEvent, waitFor, act } from '@testing-library/react-native';
import { PaperProvider } from 'react-native-paper';
import { theme } from '../../config/theme';

// Inline minimal mock of the milk tab (real screen needs router/i18n; this tests the core logic)
// If you have a test wrapper that provides these, replace this block with the real screen.
jest.mock('expo-router', () => ({
  useRouter: () => ({ push: jest.fn(), back: jest.fn() }),
  useLocalSearchParams: () => ({}),
  Stack: { Screen: () => null },
}));

jest.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (k: string) => k }),
}));

// eslint-disable-next-line @typescript-eslint/no-var-requires
const MilkTab = require('../../../app/(tabs)/milk').default;

const wrap = (ui: React.ReactElement) => (
  <PaperProvider theme={theme}>{ui}</PaperProvider>
);

describe('Milk Recording Flow', () => {
  it('renders session selector and numpad', () => {
    const { getByText } = render(wrap(<MilkTab />));
    expect(getByText(/Morning|☀️/i)).toBeTruthy();
    expect(getByText(/Evening|🌙/i)).toBeTruthy();
    // Numpad keys
    expect(getByText('1')).toBeTruthy();
    expect(getByText('0')).toBeTruthy();
  });

  it('Record button is disabled when no animal or quantity selected', () => {
    const { getByTestId } = render(wrap(<MilkTab />));
    const recordBtn = getByTestId('record-milk-btn');
    expect(recordBtn.props.accessibilityState?.disabled).toBe(true);
  });

  it('enables Record button after selecting animal and entering quantity', async () => {
    const { getByTestId, getByText } = render(wrap(<MilkTab />));
    // Select first animal chip
    fireEvent.press(getByTestId('animal-chip-0'));
    // Enter quantity via numpad
    fireEvent.press(getByText('1'));
    fireEvent.press(getByText('2'));

    await waitFor(() => {
      const btn = getByTestId('record-milk-btn');
      expect(btn.props.accessibilityState?.disabled).toBe(false);
    });
  });

  it('shows snackbar confirmation after successful recording', async () => {
    const { getByTestId, getByText, findByText } = render(wrap(<MilkTab />));
    fireEvent.press(getByTestId('animal-chip-0'));
    fireEvent.press(getByText('5'));

    fireEvent.press(getByTestId('record-milk-btn'));

    const confirmation = await findByText(/recorded|ದಾಖಲಿಸಲಾಗಿದೆ/i);
    expect(confirmation).toBeTruthy();
  });

  it('backspace removes last digit from quantity', () => {
    const { getByText, getByTestId } = render(wrap(<MilkTab />));
    fireEvent.press(getByText('1'));
    fireEvent.press(getByText('5'));
    fireEvent.press(getByText('⌫'));
    expect(getByTestId('quantity-display').props.children).toBe('1');
  });

  it('switching session clears quantity', async () => {
    const { getByText, getByTestId } = render(wrap(<MilkTab />));
    fireEvent.press(getByText('8'));
    fireEvent.press(getByText(/Evening|🌙/i));
    await waitFor(() => {
      expect(getByTestId('quantity-display').props.children).toBe('0');
    });
  });
});
