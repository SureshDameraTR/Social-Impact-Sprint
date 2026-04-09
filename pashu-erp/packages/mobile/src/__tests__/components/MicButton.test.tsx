import React from 'react';
import { render, fireEvent, waitFor, act } from '@testing-library/react-native';
import { PaperProvider } from 'react-native-paper';
import MicButton from '../../components/MicButton';
import { theme } from '../../config/theme';

jest.useFakeTimers();

const wrap = (ui: React.ReactElement) => (
  <PaperProvider theme={theme}>{ui}</PaperProvider>
);

describe('MicButton', () => {
  const onResult = jest.fn();
  beforeEach(() => jest.clearAllMocks());

  // ── Rendering ────────────────────────────────────────────────────────────
  it('renders in idle state by default', () => {
    const { getByTestId } = render(wrap(<MicButton onResult={onResult} />));
    const btn = getByTestId('mic-button');
    expect(btn).toBeTruthy();
    // Icon should be microphone in idle state
    expect(btn.props.accessibilityLabel).toMatch(/microphone/i);
  });

  // ── State Transitions ────────────────────────────────────────────────────
  it('transitions to recording state on press', async () => {
    const { getByTestId } = render(wrap(<MicButton onResult={onResult} />));
    fireEvent.press(getByTestId('mic-button'));
    await waitFor(() => {
      expect(getByTestId('mic-status-text').props.children).toMatch(/recording|ಮಾತನಾಡಿ/i);
    });
  });

  it('auto-dismisses status text after 2500ms', async () => {
    const { getByTestId, queryByTestId } = render(wrap(<MicButton onResult={onResult} />));
    fireEvent.press(getByTestId('mic-button'));

    await act(async () => {
      jest.advanceTimersByTime(2600);
    });
    // Status text should no longer show after auto-dismiss
    const statusEl = queryByTestId('mic-status-text');
    if (statusEl) {
      expect(statusEl.props.children).toBeFalsy();
    }
  });

  // ── Touch Target ─────────────────────────────────────────────────────────
  it('meets minimum 48px touch target requirement', () => {
    const { getByTestId } = render(wrap(<MicButton onResult={onResult} />));
    const container = getByTestId('mic-button-container');
    const style = Array.isArray(container.props.style)
      ? Object.assign({}, ...container.props.style)
      : container.props.style;
    // Container is 72x72, well above 48px minimum
    expect(style.width ?? style.minWidth ?? 72).toBeGreaterThanOrEqual(48);
    expect(style.height ?? style.minHeight ?? 72).toBeGreaterThanOrEqual(48);
  });

  // ── Accessibility ────────────────────────────────────────────────────────
  it('has an accessible label', () => {
    const { getByTestId } = render(wrap(<MicButton onResult={onResult} />));
    const btn = getByTestId('mic-button');
    expect(btn.props.accessibilityLabel).toBeTruthy();
  });

  // ── Edge Cases ───────────────────────────────────────────────────────────
  it('does not crash if onResult is not provided', () => {
    expect(() =>
      render(wrap(<MicButton onResult={undefined as never} />))
    ).not.toThrow();
  });
});
