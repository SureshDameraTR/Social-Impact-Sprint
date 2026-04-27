/**
 * Login screen tests.
 *
 * Verifies: rendering, phone input, OTP flow gating,
 * button disabled states, and accessibility.
 */

// ---- Mocks (must be before any imports that use them) ----
jest.mock('expo-router', () => ({
  router: { push: jest.fn(), replace: jest.fn(), back: jest.fn() },
}));

jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: 'en', changeLanguage: jest.fn() },
  }),
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

const LoginScreen = require('../../../app/(auth)/login').default;

const wrap = (ui: React.ReactElement) => (
  <PaperProvider theme={theme}>{ui}</PaperProvider>
);

describe('LoginScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // ---- Rendering ----

  it('renders the PashuRaksha title', () => {
    const { getByText } = render(wrap(<LoginScreen />));
    expect(getByText('PashuRaksha')).toBeTruthy();
  });

  it('renders the welcome text via i18n key', () => {
    const { getByText } = render(wrap(<LoginScreen />));
    expect(getByText('auth.welcome')).toBeTruthy();
  });

  it('renders the +91 country code prefix', () => {
    const { getByText } = render(wrap(<LoginScreen />));
    expect(getByText('+91')).toBeTruthy();
  });

  it('renders the phone input placeholder', () => {
    const { getByPlaceholderText } = render(wrap(<LoginScreen />));
    expect(getByPlaceholderText('auth.enterPhone')).toBeTruthy();
  });

  // ---- Phone input ----

  it('accepts a 10-digit phone number', () => {
    const { getByPlaceholderText } = render(wrap(<LoginScreen />));
    const phoneInput = getByPlaceholderText('auth.enterPhone');
    fireEvent.changeText(phoneInput, '9876543210');
    expect(phoneInput.props.value).toBe('9876543210');
  });

  it('shows Send OTP button text', () => {
    const { getByText } = render(wrap(<LoginScreen />));
    expect(getByText('auth.sendOtp')).toBeTruthy();
  });

  // ---- OTP section ----

  it('does not show OTP input boxes initially', () => {
    const { queryByText } = render(wrap(<LoginScreen />));
    expect(queryByText('auth.enterOtp')).toBeNull();
  });

  it('shows OTP section after successful send', async () => {
    (global as any).fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ message: 'OTP sent' }),
    });

    const { getByPlaceholderText, getByText, findByText } = render(
      wrap(<LoginScreen />)
    );

    fireEvent.changeText(getByPlaceholderText('auth.enterPhone'), '9876543210');
    fireEvent.press(getByText('auth.sendOtp'));

    expect(await findByText('auth.enterOtp')).toBeTruthy();
  });

  it('switches button text to Verify OTP after sending', async () => {
    (global as any).fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ message: 'OTP sent' }),
    });

    const { getByPlaceholderText, getByText, findByText } = render(
      wrap(<LoginScreen />)
    );

    fireEvent.changeText(getByPlaceholderText('auth.enterPhone'), '9876543210');
    fireEvent.press(getByText('auth.sendOtp'));

    expect(await findByText('auth.verifyOtp')).toBeTruthy();
  });

  // ---- OTP accessibility ----

  it('OTP boxes have accessibility labels', async () => {
    (global as any).fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ message: 'OTP sent' }),
    });

    const { getByPlaceholderText, getByText, findByLabelText } = render(
      wrap(<LoginScreen />)
    );

    fireEvent.changeText(getByPlaceholderText('auth.enterPhone'), '9876543210');
    fireEvent.press(getByText('auth.sendOtp'));

    expect(await findByLabelText('OTP digit 1 of 6')).toBeTruthy();
    expect(await findByLabelText('OTP digit 6 of 6')).toBeTruthy();
  });

  // ---- Error handling ----

  it('shows error when OTP request fails', async () => {
    (global as any).fetch = jest.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ detail: 'Rate limited' }),
    });

    const { getByPlaceholderText, getByText, findByText } = render(
      wrap(<LoginScreen />)
    );

    fireEvent.changeText(getByPlaceholderText('auth.enterPhone'), '9876543210');
    fireEvent.press(getByText('auth.sendOtp'));

    expect(await findByText('Rate limited')).toBeTruthy();
  });
});
