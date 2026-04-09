import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { PaperProvider } from 'react-native-paper';
import TriageCard from '../../components/TriageCard';
import { theme } from '../../config/theme';

const wrap = (ui: React.ReactElement) => (
  <PaperProvider theme={theme}>{ui}</PaperProvider>
);

const baseProps = {
  animalName: 'Ganga',
  symptoms: ['fever', 'nasal_discharge'],
  severity: 'high' as const,
  recommendation: 'Contact veterinarian within 24 hours',
  onCallVet: jest.fn(),
};

describe('TriageCard', () => {
  beforeEach(() => jest.clearAllMocks());

  // ── Rendering ────────────────────────────────────────────────────────────
  it('renders animal name and recommendation', () => {
    const { getByText } = render(wrap(<TriageCard {...baseProps} />));
    expect(getByText('Ganga')).toBeTruthy();
    expect(getByText(/Contact veterinarian/i)).toBeTruthy();
  });

  // ── Severity States ──────────────────────────────────────────────────────
  it.each([
    ['critical', '#C62828', true],
    ['high', '#E65100', true],
    ['medium', '#F57F17', false],
    ['low', '#2E7D32', false],
  ] as const)(
    '%s severity: correct badge color, Call Vet button visible=%s',
    (severity, expectedColor, showsCallVet) => {
      const { queryByText, getByTestId } = render(
        wrap(<TriageCard {...baseProps} severity={severity} />)
      );
      const badge = getByTestId('severity-badge');
      expect(badge.props.style).toMatchObject(
        expect.objectContaining({ backgroundColor: expectedColor })
      );
      if (showsCallVet) {
        expect(queryByText(/Call Vet/i)).toBeTruthy();
      } else {
        expect(queryByText(/Call Vet/i)).toBeNull();
      }
    }
  );

  // ── Interaction ──────────────────────────────────────────────────────────
  it('triggers onCallVet when Call Vet button is pressed on critical', () => {
    const props = { ...baseProps, severity: 'critical' as const };
    const { getByText } = render(wrap(<TriageCard {...props} />));
    fireEvent.press(getByText(/Call Vet/i));
    expect(baseProps.onCallVet).toHaveBeenCalledTimes(1);
  });

  it('does not render Call Vet button for medium/low severity', () => {
    const { queryByText } = render(
      wrap(<TriageCard {...baseProps} severity="medium" />)
    );
    expect(queryByText(/Call Vet/i)).toBeNull();
  });

  // ── Edge Cases ───────────────────────────────────────────────────────────
  it('handles empty symptoms array', () => {
    expect(() =>
      render(wrap(<TriageCard {...baseProps} symptoms={[]} />))
    ).not.toThrow();
  });

  it('handles very long recommendation text', () => {
    const longRec = 'Administer antibiotic '.repeat(20);
    expect(() =>
      render(wrap(<TriageCard {...baseProps} recommendation={longRec} />))
    ).not.toThrow();
  });
});
