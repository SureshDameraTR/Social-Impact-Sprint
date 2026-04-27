/**
 * Home (tabs/index) screen tests.
 *
 * Verifies: rendering, translated greeting, quick actions,
 * animal list, loading/error states, and FAB.
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
  post: jest.fn(),
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

// ---- Imports ----
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { PaperProvider } from 'react-native-paper';
import { theme } from '../../config/theme';

const HomeScreen = require('../../../app/(tabs)/index').default;

const wrap = (ui: React.ReactElement) => (
  <PaperProvider theme={theme}>{ui}</PaperProvider>
);

const mockAnimals = [
  { id: '1', name: 'Ganga', species: 'cattle', breed: 'HF Cross', tagNumber: 'KA-001', healthStatus: 'healthy' },
  { id: '2', name: 'Nandi', species: 'cattle', breed: 'Jersey', tagNumber: 'KA-002', healthStatus: 'sick' },
];

describe('HomeScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // ---- Loading state ----

  it('shows loading text while fetching animals', () => {
    mockApi.get.mockReturnValue(new Promise(() => {}));
    const { getByText } = render(wrap(<HomeScreen />));
    expect(getByText('common.loading')).toBeTruthy();
  });

  // ---- Successful data load ----

  it('renders greeting text after data loads', async () => {
    mockApi.get.mockResolvedValue(mockAnimals);
    const { findByText } = render(wrap(<HomeScreen />));
    const greeting = await findByText(/home\.greeting/);
    expect(greeting).toBeTruthy();
  });

  it('renders subtitle after data loads', async () => {
    mockApi.get.mockResolvedValue(mockAnimals);
    const { findByText } = render(wrap(<HomeScreen />));
    expect(await findByText('home.subtitle')).toBeTruthy();
  });

  it('displays My Animals section title', async () => {
    mockApi.get.mockResolvedValue(mockAnimals);
    const { findByText } = render(wrap(<HomeScreen />));
    expect(await findByText('animals.myAnimals')).toBeTruthy();
  });

  it('shows animal count', async () => {
    mockApi.get.mockResolvedValue(mockAnimals);
    const { findByText } = render(wrap(<HomeScreen />));
    expect(await findByText(/2/)).toBeTruthy();
  });

  // ---- Quick actions ----

  it('renders quick action buttons', async () => {
    mockApi.get.mockResolvedValue(mockAnimals);
    const { findByText } = render(wrap(<HomeScreen />));
    expect(await findByText('home.addMilk')).toBeTruthy();
    expect(await findByText('home.healthCheck')).toBeTruthy();
  });

  it('quick actions have accessibility labels', async () => {
    mockApi.get.mockResolvedValue(mockAnimals);
    const { findByLabelText } = render(wrap(<HomeScreen />));
    expect(await findByLabelText('Add milk record')).toBeTruthy();
    expect(await findByLabelText('Health check')).toBeTruthy();
  });

  // ---- Error state ----

  it('shows error state when API call fails', async () => {
    mockApi.get.mockRejectedValue(new Error('Network error'));
    const { findByText } = render(wrap(<HomeScreen />));
    expect(await findByText('common.error')).toBeTruthy();
  });

  it('shows retry button on error', async () => {
    mockApi.get.mockRejectedValue(new Error('Network error'));
    const { findByText } = render(wrap(<HomeScreen />));
    expect(await findByText('common.retry')).toBeTruthy();
  });

  it('retries fetch when retry button is pressed', async () => {
    mockApi.get
      .mockRejectedValueOnce(new Error('fail'))
      .mockResolvedValueOnce(mockAnimals);

    const { findByText } = render(wrap(<HomeScreen />));
    const retryBtn = await findByText('common.retry');
    fireEvent.press(retryBtn);

    expect(mockApi.get).toHaveBeenCalledTimes(2);
  });

  // ---- Empty state ----

  it('shows empty state when no animals exist', async () => {
    mockApi.get.mockResolvedValue([]);
    const { findByText } = render(wrap(<HomeScreen />));
    expect(await findByText('empty.noAnimals')).toBeTruthy();
    expect(await findByText('empty.addFirst')).toBeTruthy();
  });

  // ---- FAB ----

  it('renders the Add Animal FAB', async () => {
    mockApi.get.mockResolvedValue(mockAnimals);
    const { findByText } = render(wrap(<HomeScreen />));
    expect(await findByText('animals.addAnimal')).toBeTruthy();
  });
});
