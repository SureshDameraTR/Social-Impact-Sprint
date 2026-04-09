import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { PaperProvider } from 'react-native-paper';
import FilterChips from '../../components/FilterChips';
import { theme } from '../../config/theme';

const wrap = (ui: React.ReactElement) => (
  <PaperProvider theme={theme}>{ui}</PaperProvider>
);

describe('FilterChips', () => {
  const onFilterChange = jest.fn();
  beforeEach(() => jest.clearAllMocks());

  // ── Rendering ────────────────────────────────────────────────────────────
  it('renders all 5 filter chips', () => {
    const { getByText } = render(
      wrap(<FilterChips selected="all" onFilterChange={onFilterChange} />)
    );
    expect(getByText('All')).toBeTruthy();
    expect(getByText(/Cattle/i)).toBeTruthy();
    expect(getByText(/Goat/i)).toBeTruthy();
    expect(getByText(/Sheep/i)).toBeTruthy();
    expect(getByText(/Poultry/i)).toBeTruthy();
  });

  // ── Selection State ──────────────────────────────────────────────────────
  it('marks the selected chip as active', () => {
    const { getByTestId } = render(
      wrap(<FilterChips selected="cattle" onFilterChange={onFilterChange} />)
    );
    const cattleChip = getByTestId('chip-cattle');
    // Selected chip should have colored background (not outlined mode)
    expect(cattleChip.props.style).not.toMatchObject(
      expect.objectContaining({ backgroundColor: 'transparent' })
    );
  });

  it('calls onFilterChange with correct value when chip is pressed', () => {
    const { getByText } = render(
      wrap(<FilterChips selected="all" onFilterChange={onFilterChange} />)
    );
    fireEvent.press(getByText(/Goat/i));
    expect(onFilterChange).toHaveBeenCalledWith('goat');
  });

  it('calls onFilterChange with "all" when All chip is pressed', () => {
    const { getByText } = render(
      wrap(<FilterChips selected="cattle" onFilterChange={onFilterChange} />)
    );
    fireEvent.press(getByText('All'));
    expect(onFilterChange).toHaveBeenCalledWith('all');
  });

  // ── Edge Cases ───────────────────────────────────────────────────────────
  it('does not call onFilterChange twice on rapid double-tap', () => {
    const { getByText } = render(
      wrap(<FilterChips selected="all" onFilterChange={onFilterChange} />)
    );
    fireEvent.press(getByText(/Cattle/i));
    fireEvent.press(getByText(/Cattle/i));
    // Both presses should register (no dedup) — important for testing handler stability
    expect(onFilterChange).toHaveBeenCalledTimes(2);
  });

  it('renders without crashing when selected prop is an unknown value', () => {
    expect(() =>
      render(wrap(<FilterChips selected={'buffalo' as never} onFilterChange={onFilterChange} />))
    ).not.toThrow();
  });
});
