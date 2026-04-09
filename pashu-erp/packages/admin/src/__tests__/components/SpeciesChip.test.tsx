import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import SpeciesChip from '../../components/SpeciesChip';
import { adminTheme } from '../../theme/theme';

const wrap = (ui: React.ReactElement) => (
  <ThemeProvider theme={adminTheme}>{ui}</ThemeProvider>
);

describe('SpeciesChip', () => {
  it.each([
    ['Cattle', '🐄'],
    ['Buffalo', '🐃'],
    ['Goat', '🐐'],
    ['Sheep', '🐑'],
    ['Poultry', '🐔'],
    ['Pig', '🐖'],
  ])('%s: renders correct emoji and label', (species, emoji) => {
    render(wrap(<SpeciesChip species={species} />));
    expect(screen.getByText(new RegExp(`${emoji}.*${species}`))).toBeInTheDocument();
  });

  it('renders unknown species with default paw emoji', () => {
    render(wrap(<SpeciesChip species="Alpaca" />));
    expect(screen.getByText(/🐾.*Alpaca/)).toBeInTheDocument();
  });

  it('renders as small chip', () => {
    render(wrap(<SpeciesChip species="Cattle" />));
    expect(screen.getByText(/🐄.*Cattle/).closest('[class*="MuiChip-sizeSmall"]')).toBeTruthy();
  });

  it('handles empty species string without crashing', () => {
    expect(() => render(wrap(<SpeciesChip species="" />))).not.toThrow();
  });
});
