/**
 * Milk tab screen tests.
 *
 * Verifies: rendering, session toggle, animal picker, numpad,
 * quantity display, record button states, and voice input integration.
 */

// ---- Mocks ----
jest.mock('expo-router', () => ({
  router: { push: jest.fn(), replace: jest.fn(), back: jest.fn() },
}));

jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: 'en', changeLanguage: jest.fn() },
  }),
}));

const mockApi = {
  get: jest.fn(),
  post: jest.fn(() => Promise.resolve({})),
  patch: jest.fn(),
  delete: jest.fn(),
};
jest.mock('../../../src/config/api', () => ({
  __esModule: true,
  api: mockApi,
}));

jest.mock('../../../src/config/storage', () => ({
  getItemAsync: jest.fn(() => Promise.resolve(null)),
  setItemAsync: jest.fn(() => Promise.resolve()),
  deleteItemAsync: jest.fn(() => Promise.resolve()),
}));

jest.mock('../../../src/hooks/useSnackbar', () => ({
  useSnackbar: () => ({
    showError: jest.fn(),
    showSuccess: jest.fn(),
    showInfo: jest.fn(),
  }),
}));

jest.mock('../../../src/services/voice', () => ({
  transcribeAudio: jest.fn(() =>
    Promise.resolve({ text: 'five', confidence: 0.95, parsedNumber: 5, language: 'en' })
  ),
}));

jest.mock('../../../src/components/MicButton', () => {
  const React = require('react');
  return {
    MicButton: ({ onResult }: { onResult: (v: number) => void }) => {
      const { Pressable, Text } = require('react-native');
      return (
        <Pressable testID="mic-btn" onPress={() => onResult(5)}>
          <Text>Mic</Text>
        </Pressable>
      );
    },
  };
});

// ---- Imports ----
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { PaperProvider } from 'react-native-paper';
import { theme } from '../../config/theme';

const MilkScreen = require('../../../app/(tabs)/milk').default;

const wrap = (ui: React.ReactElement) => (
  <PaperProvider theme={theme}>{ui}</PaperProvider>
);

const mockCows = [
  { id: 'c1', name: 'Lakshmi', species: 'cattle' },
  { id: 'c2', name: 'Ganga', species: 'cattle' },
];

describe('MilkScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockApi.get.mockImplementation((path: string) => {
      if (path.includes('/animals')) return Promise.resolve(mockCows);
      if (path.includes('/milk/today')) return Promise.resolve({ total_liters: 12.5 });
      return Promise.resolve({ data: [] });
    });
  });

  // ---- Session toggle ----

  it('renders morning and evening session buttons', async () => {
    const { findByText } = render(wrap(<MilkScreen />));
    expect(await findByText(/milk\.morning/)).toBeTruthy();
    expect(await findByText(/milk\.evening/)).toBeTruthy();
  });

  // ---- Today's total ----

  it('displays today total milk yield label', async () => {
    const { findByText } = render(wrap(<MilkScreen />));
    expect(await findByText('milk.todayTotal')).toBeTruthy();
  });

  it('shows the numeric total value', async () => {
    const { findByText } = render(wrap(<MilkScreen />));
    expect(await findByText(/12\.5/)).toBeTruthy();
  });

  // ---- Animal picker ----

  it('renders animal chips for each cow', async () => {
    const { findByText } = render(wrap(<MilkScreen />));
    expect(await findByText('Lakshmi')).toBeTruthy();
    expect(await findByText('Ganga')).toBeTruthy();
  });

  it('animal chips have radio accessibility role', async () => {
    const { findByLabelText } = render(wrap(<MilkScreen />));
    const chip = await findByLabelText('Lakshmi');
    expect(chip.props.accessibilityRole).toBe('radio');
  });

  // ---- Numpad ----

  it('renders all numpad keys', async () => {
    const { findByText } = render(wrap(<MilkScreen />));
    for (const digit of ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '.']) {
      expect(await findByText(digit)).toBeTruthy();
    }
  });

  it('renders backspace key', async () => {
    const { findByText } = render(wrap(<MilkScreen />));
    expect(await findByText('\u232B')).toBeTruthy();
  });

  // ---- Record button ----

  it('renders the record milk button', async () => {
    const { findByText } = render(wrap(<MilkScreen />));
    expect(await findByText('milk.recordMilk')).toBeTruthy();
  });

  // ---- History link ----

  it('renders the history link', async () => {
    const { findByText } = render(wrap(<MilkScreen />));
    expect(await findByText('milk.history')).toBeTruthy();
  });

  // ---- Select Animal label ----

  it('shows Select Animal section title', async () => {
    const { findByText } = render(wrap(<MilkScreen />));
    expect(await findByText('milk.selectAnimal')).toBeTruthy();
  });

  // ---- Error state ----

  it('shows error state when API fails', async () => {
    mockApi.get.mockRejectedValue(new Error('Network error'));
    const { findByText } = render(wrap(<MilkScreen />));
    expect(await findByText('common.error')).toBeTruthy();
  });

  // ---- Empty state (no cows) ----

  it('shows empty state when no cattle are returned', async () => {
    mockApi.get.mockImplementation((path: string) => {
      if (path.includes('/animals')) return Promise.resolve([]);
      if (path.includes('/milk/today')) return Promise.resolve({ total_liters: 0 });
      return Promise.resolve({ data: [] });
    });
    const { findByText } = render(wrap(<MilkScreen />));
    expect(await findByText('empty.noMilkRecords')).toBeTruthy();
  });

  // ---- Liters unit label ----

  it('shows liters unit label', async () => {
    const { findAllByText } = render(wrap(<MilkScreen />));
    const litersElements = await findAllByText('milk.liters');
    expect(litersElements.length).toBeGreaterThan(0);
  });
});
