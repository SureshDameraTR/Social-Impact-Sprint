import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import RiskBadge from '../../components/RiskBadge';
import { adminTheme, colors } from '../../theme/theme';

const wrap = (ui: React.ReactElement) => (
  <ThemeProvider theme={adminTheme}>{ui}</ThemeProvider>
);

describe('RiskBadge', () => {
  // ── All four severity levels ─────────────────────────────────────────────
  it.each([
    ['critical', 'Critical', colors.errorLight, colors.accentRed],
    ['high', 'High', colors.warningLight, colors.accentAmber],
    ['medium', 'Medium', colors.infoLight, colors.accentBlue],
    ['low', 'Low', colors.successLight, colors.accentGreen],
  ] as const)(
    '%s: label, background and text color are correct',
    (level, label, bg, textColor) => {
      render(wrap(<RiskBadge level={level} />));
      const chip = screen.getByText(label);
      expect(chip).toBeInTheDocument();
      // Chip container styling
      const chipEl = chip.closest('[class*="MuiChip"]') as HTMLElement;
      expect(chipEl).toHaveStyle({ backgroundColor: bg });
      expect(chip).toHaveStyle({ color: textColor });
    }
  );

  // ── Size prop ────────────────────────────────────────────────────────────
  it('renders small size by default', () => {
    render(wrap(<RiskBadge level="medium" />));
    const chipEl = screen.getByText('Medium').closest('[class*="MuiChip-sizeSmall"]');
    expect(chipEl).toBeTruthy();
  });

  it('renders medium size when specified', () => {
    render(wrap(<RiskBadge level="medium" size="medium" />));
    // Should not have sizeSmall class
    const chipEl = screen.getByText('Medium').closest('[class*="MuiChip-sizeMedium"]');
    expect(chipEl).toBeTruthy();
  });

  // ── Edge Cases ───────────────────────────────────────────────────────────
  it('renders without crashing for all known levels', () => {
    const levels = ['critical', 'high', 'medium', 'low'] as const;
    levels.forEach((level) => {
      expect(() => render(wrap(<RiskBadge level={level} />))).not.toThrow();
    });
  });
});
