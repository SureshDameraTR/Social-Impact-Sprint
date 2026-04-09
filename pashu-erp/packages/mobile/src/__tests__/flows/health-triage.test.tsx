/**
 * Integration test: Health Triage Flow
 * Flow: Select animal → select symptoms → Check Health → see triage result → optionally Call Vet
 */
import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { PaperProvider } from 'react-native-paper';
import { theme } from '../../config/theme';

jest.mock('expo-router', () => ({
  useRouter: () => ({ push: jest.fn(), back: jest.fn() }),
  useLocalSearchParams: () => ({}),
  Stack: { Screen: () => null },
}));
jest.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (k: string) => k }),
}));

// eslint-disable-next-line @typescript-eslint/no-var-requires
const HealthTab = require('../../../app/(tabs)/health').default;

const wrap = (ui: React.ReactElement) => (
  <PaperProvider theme={theme}>{ui}</PaperProvider>
);

describe('Health Triage Flow', () => {
  it('renders animal selector and symptom grid', () => {
    const { getByTestId } = render(wrap(<HealthTab />));
    expect(getByTestId('animal-selector')).toBeTruthy();
    expect(getByTestId('symptom-grid')).toBeTruthy();
  });

  it('Check Health button is disabled when no symptoms selected', () => {
    const { getByTestId } = render(wrap(<HealthTab />));
    expect(getByTestId('check-health-btn').props.accessibilityState?.disabled).toBe(true);
  });

  it('enables Check Health button after animal + symptom selection', async () => {
    const { getByTestId } = render(wrap(<HealthTab />));
    fireEvent.press(getByTestId('animal-chip-0'));
    fireEvent.press(getByTestId('symptom-fever'));

    await waitFor(() => {
      expect(getByTestId('check-health-btn').props.accessibilityState?.disabled).toBe(false);
    });
  });

  it('shows triage result card after checking health', async () => {
    const { getByTestId, findByTestId } = render(wrap(<HealthTab />));
    fireEvent.press(getByTestId('animal-chip-0'));
    fireEvent.press(getByTestId('symptom-fever'));
    fireEvent.press(getByTestId('symptom-loss_of_appetite'));

    fireEvent.press(getByTestId('check-health-btn'));

    const triageCard = await findByTestId('triage-result');
    expect(triageCard).toBeTruthy();
  });

  it('Reset clears all selected symptoms', async () => {
    const { getByTestId, getByText } = render(wrap(<HealthTab />));
    fireEvent.press(getByTestId('animal-chip-0'));
    fireEvent.press(getByTestId('symptom-fever'));
    fireEvent.press(getByText(/Reset|ಮರುಹೊಂದಿಸಿ/i));

    await waitFor(() => {
      // Symptoms chip should return to unselected state
      const symptomChip = getByTestId('symptom-fever');
      expect(symptomChip.props.style).not.toMatchObject(
        expect.objectContaining({ borderColor: '#C62828' })
      );
    });
  });

  it('multiple symptoms can be selected simultaneously', () => {
    const { getByTestId } = render(wrap(<HealthTab />));
    fireEvent.press(getByTestId('symptom-fever'));
    fireEvent.press(getByTestId('symptom-nasal_discharge'));
    fireEvent.press(getByTestId('symptom-loss_of_appetite'));
    // All 3 should remain visually selected — no single-select behavior
    expect(getByTestId('symptom-fever').props.style).toMatchObject(
      expect.objectContaining({ borderColor: '#C62828' })
    );
    expect(getByTestId('symptom-nasal_discharge').props.style).toMatchObject(
      expect.objectContaining({ borderColor: '#C62828' })
    );
  });
});
