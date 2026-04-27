/**
 * Profile screen tests.
 *
 * Verifies: rendering, language selector, farm details,
 * quick stats, logout button, loading/error states.
 */

// ---- Mocks ----
const mockRouter = { push: jest.fn(), replace: jest.fn(), back: jest.fn() };
jest.mock('expo-router', () => ({
  router: mockRouter,
}));

jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: {
      language: 'en',
      changeLanguage: jest.fn(),
      hasResourceBundle: jest.fn(() => false),
      addResourceBundle: jest.fn(),
    },
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

const mockStorage = {
  getItemAsync: jest.fn(() => Promise.resolve(null)),
  setItemAsync: jest.fn(() => Promise.resolve()),
  deleteItemAsync: jest.fn(() => Promise.resolve()),
};
jest.mock('../../../src/config/storage', () => mockStorage);

jest.mock('../../../src/i18n', () => ({
  __esModule: true,
  default: { use: jest.fn().mockReturnThis(), init: jest.fn(), language: 'en' },
  loadLanguage: jest.fn(),
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

const ProfileScreen = require('../../../app/profile').default;

const wrap = (ui: React.ReactElement) => (
  <PaperProvider theme={theme}>{ui}</PaperProvider>
);

const mockProfile = {
  name: 'Lakshamma',
  phone: '+919876543210',
  village: 'Hoskote',
  totalAnimals: 5,
  farmSize: '2 acres',
  memberSince: 'Jan 2025',
  todayMilk: 18.5,
  monthlyIncome: 25000,
};

describe('ProfileScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockApi.get.mockResolvedValue(mockProfile);
  });

  // ---- Loading state ----

  it('renders without crashing during loading', () => {
    mockApi.get.mockReturnValue(new Promise(() => {}));
    expect(() => render(wrap(<ProfileScreen />))).not.toThrow();
  });

  // ---- Profile data ----

  it('displays the user name after loading', async () => {
    const { findByText } = render(wrap(<ProfileScreen />));
    expect(await findByText('Lakshamma')).toBeTruthy();
  });

  it('displays the village name', async () => {
    const { findByText } = render(wrap(<ProfileScreen />));
    expect(await findByText('Hoskote')).toBeTruthy();
  });

  // ---- Language selector ----

  it('renders the language selector card', async () => {
    const { findByText } = render(wrap(<ProfileScreen />));
    expect(await findByText('onboarding.selectLanguage')).toBeTruthy();
  });

  it('renders English language button', async () => {
    const { findByText } = render(wrap(<ProfileScreen />));
    expect(await findByText('English')).toBeTruthy();
  });

  // ---- Farm details ----

  it('renders farm details card title', async () => {
    const { findByText } = render(wrap(<ProfileScreen />));
    expect(await findByText(/profile\.farmDetails/)).toBeTruthy();
  });

  it('displays total animals count', async () => {
    const { findByText } = render(wrap(<ProfileScreen />));
    expect(await findByText('animals.totalAnimals')).toBeTruthy();
    expect(await findByText('5')).toBeTruthy();
  });

  it('displays farm size', async () => {
    const { findByText } = render(wrap(<ProfileScreen />));
    expect(await findByText('profile.farmSize')).toBeTruthy();
    expect(await findByText('2 acres')).toBeTruthy();
  });

  it('displays member since date', async () => {
    const { findByText } = render(wrap(<ProfileScreen />));
    expect(await findByText('profile.memberSince')).toBeTruthy();
    expect(await findByText('Jan 2025')).toBeTruthy();
  });

  // ---- Quick stats ----

  it('displays today milk stat', async () => {
    const { findByText } = render(wrap(<ProfileScreen />));
    expect(await findByText('18.5L')).toBeTruthy();
  });

  it('displays monthly income stat', async () => {
    const { findByText } = render(wrap(<ProfileScreen />));
    expect(await findByText(/25\.0K/)).toBeTruthy();
  });

  // ---- Logout ----

  it('renders logout button', async () => {
    const { findByText } = render(wrap(<ProfileScreen />));
    expect(await findByText('profile.logout')).toBeTruthy();
  });

  it('clears auth token and redirects on logout', async () => {
    const { findByText } = render(wrap(<ProfileScreen />));
    const logoutBtn = await findByText('profile.logout');
    fireEvent.press(logoutBtn);

    await waitFor(() => {
      expect(mockStorage.deleteItemAsync).toHaveBeenCalledWith('auth_token');
      expect(mockRouter.replace).toHaveBeenCalledWith('/(auth)/login');
    });
  });

  // ---- Error state ----

  it('shows error state when profile fetch fails', async () => {
    mockApi.get.mockRejectedValue(new Error('Server error'));
    const { findByText } = render(wrap(<ProfileScreen />));
    expect(await findByText('common.error')).toBeTruthy();
  });

  it('shows retry button on error', async () => {
    mockApi.get.mockRejectedValue(new Error('Server error'));
    const { findByText } = render(wrap(<ProfileScreen />));
    expect(await findByText('common.retry')).toBeTruthy();
  });
});
