import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { PaperProvider } from 'react-native-paper';
import AnimalCard from '../../components/AnimalCard';
import { theme } from '../../config/theme';

const wrap = (ui: React.ReactElement) => (
  <PaperProvider theme={theme}>{ui}</PaperProvider>
);

const baseProps = {
  id: '1',
  name: 'Ganga',
  species: 'cattle' as const,
  breed: 'HF Cross',
  age: '3 yrs',
  health: 'healthy' as const,
  lastMilk: '12L',
  tag: 'KA-001',
  onPress: jest.fn(),
};

describe('AnimalCard', () => {
  beforeEach(() => jest.clearAllMocks());

  // ── Rendering ────────────────────────────────────────────────────────────
  it('renders animal name', () => {
    const { getByText } = render(wrap(<AnimalCard {...baseProps} />));
    expect(getByText('Ganga')).toBeTruthy();
  });

  it('renders breed and age', () => {
    const { getByText } = render(wrap(<AnimalCard {...baseProps} />));
    expect(getByText(/HF Cross/i)).toBeTruthy();
  });

  it('renders without crashing with minimal required props', () => {
    expect(() => render(wrap(<AnimalCard {...baseProps} />))).not.toThrow();
  });

  // ── Interaction ──────────────────────────────────────────────────────────
  it('calls onPress with animal id when tapped', () => {
    const { getByTestId } = render(wrap(<AnimalCard {...baseProps} testID="animal-card" />));
    fireEvent.press(getByTestId('animal-card'));
    expect(baseProps.onPress).toHaveBeenCalledWith('1');
  });

  it('onPress is called exactly once per tap', () => {
    const { getByTestId } = render(wrap(<AnimalCard {...baseProps} testID="animal-card" />));
    fireEvent.press(getByTestId('animal-card'));
    fireEvent.press(getByTestId('animal-card'));
    expect(baseProps.onPress).toHaveBeenCalledTimes(2);
  });

  // ── Health State ─────────────────────────────────────────────────────────
  it('shows green health indicator for healthy animals', () => {
    const { getByTestId } = render(wrap(<AnimalCard {...baseProps} testID="animal-card" />));
    // Health dot should use healthy color
    const healthDot = getByTestId('health-dot');
    expect(healthDot.props.style).toMatchObject(
      expect.objectContaining({ backgroundColor: '#2E7D32' })
    );
  });

  it('shows red health indicator for sick animals', () => {
    const props = { ...baseProps, health: 'sick' as const };
    const { getByTestId } = render(wrap(<AnimalCard {...props} testID="animal-card" />));
    const healthDot = getByTestId('health-dot');
    expect(healthDot.props.style).toMatchObject(
      expect.objectContaining({ backgroundColor: '#C62828' })
    );
  });

  // ── Species Badge ────────────────────────────────────────────────────────
  it.each([
    ['cattle', '🐄'],
    ['goat', '🐐'],
    ['sheep', '🐑'],
    ['poultry', '🐔'],
  ])('shows correct emoji for %s', (species, emoji) => {
    const { getByText } = render(
      wrap(<AnimalCard {...baseProps} species={species as never} />)
    );
    expect(getByText(new RegExp(emoji))).toBeTruthy();
  });

  // ── Edge Cases ───────────────────────────────────────────────────────────
  it('handles very long animal name without overflow crash', () => {
    const longName = 'A'.repeat(80);
    expect(() =>
      render(wrap(<AnimalCard {...baseProps} name={longName} />))
    ).not.toThrow();
  });

  it('handles special characters in name', () => {
    const { getByText } = render(
      wrap(<AnimalCard {...baseProps} name="ಗಂಗಾ <Ganga>" />)
    );
    expect(getByText(/ಗಂಗಾ/)).toBeTruthy();
  });
});
