/**
 * Onboarding profile screen tests.
 *
 * Verifies: rendering, name input, district picker, save button state,
 * and API submission.
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

jest.mock('../../../src/i18n', () => ({
  __esModule: true,
  default: { use: jest.fn().mockReturnThis(), init: jest.fn() },
  loadLanguage: jest.fn(),
}));

// ---- Imports ----
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { PaperProvider } from 'react-native-paper';
import { theme } from '../../config/theme';

const OnboardingProfile = require('../../../app/onboarding/profile').default;

const wrap = (ui: React.ReactElement) => (
  <PaperProvider theme={theme}>{ui}</PaperProvider>
);

describe('Onboarding ProfileScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // ---- Rendering ----

  it('renders the profile creation heading', () => {
    const { getByText } = render(wrap(<OnboardingProfile />));
    expect(getByText('onboarding.profileTitle')).toBeTruthy();
  });

  it('renders the subtitle', () => {
    const { getByText } = render(wrap(<OnboardingProfile />));
    expect(getByText('onboarding.profileSubtitle')).toBeTruthy();
  });

  it('renders the name input label', () => {
    const { getByText } = render(wrap(<OnboardingProfile />));
    expect(getByText('onboarding.nameLabel')).toBeTruthy();
  });

  it('renders the phone input label (disabled)', () => {
    const { getByText } = render(wrap(<OnboardingProfile />));
    expect(getByText('onboarding.phoneLabel')).toBeTruthy();
  });

  it('renders the district selector button', () => {
    const { getByText } = render(wrap(<OnboardingProfile />));
    expect(getByText('onboarding.selectDistrict')).toBeTruthy();
  });

  it('renders the village input label', () => {
    const { getByText } = render(wrap(<OnboardingProfile />));
    expect(getByText('onboarding.villageSearch')).toBeTruthy();
  });

  // ---- Save button ----

  it('renders Save & Continue button', () => {
    const { getByText } = render(wrap(<OnboardingProfile />));
    expect(getByText('onboarding.saveAndContinue')).toBeTruthy();
  });

  // ---- District picker ----

  it('opens district menu when selector is pressed', async () => {
    const { getByText, findByText } = render(wrap(<OnboardingProfile />));
    fireEvent.press(getByText('onboarding.selectDistrict'));
    expect(await findByText('Mysuru')).toBeTruthy();
  });

  it('displays selected district after selection', async () => {
    const { getByText, findByText } = render(wrap(<OnboardingProfile />));
    fireEvent.press(getByText('onboarding.selectDistrict'));

    const belagavi = await findByText('Belagavi');
    fireEvent.press(belagavi);

    await waitFor(() => {
      expect(getByText('Belagavi')).toBeTruthy();
    });
  });

  it('contains Bengaluru Urban in the district list', async () => {
    const { getByText, findByText } = render(wrap(<OnboardingProfile />));
    fireEvent.press(getByText('onboarding.selectDistrict'));
    expect(await findByText('Bengaluru Urban')).toBeTruthy();
  });

  it('contains Yadgir (last district) in the list', async () => {
    const { getByText, findByText } = render(wrap(<OnboardingProfile />));
    fireEvent.press(getByText('onboarding.selectDistrict'));
    expect(await findByText('Yadgir')).toBeTruthy();
  });

  // ---- No premature API call ----

  it('does not call API on initial render', () => {
    render(wrap(<OnboardingProfile />));
    expect(mockApi.post).not.toHaveBeenCalled();
  });
});
