import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import PeopleIcon from '@mui/icons-material/People';
import StatCard from '../../components/StatCard';
import { adminTheme } from '../../theme/theme';

const wrap = (ui: React.ReactElement) => (
  <ThemeProvider theme={adminTheme}>{ui}</ThemeProvider>
);

describe('StatCard', () => {
  const baseProps = {
    title: 'Total Farmers',
    value: '1,248',
    icon: <PeopleIcon />,
    color: '#0d6b58',
  };

  // ── Rendering ────────────────────────────────────────────────────────────
  it('renders title and value', () => {
    render(wrap(<StatCard {...baseProps} />));
    expect(screen.getByText('Total Farmers')).toBeInTheDocument();
    expect(screen.getByText('1,248')).toBeInTheDocument();
  });

  it('renders without trend chip when trend is not provided', () => {
    render(wrap(<StatCard {...baseProps} />));
    expect(screen.queryByRole('img', { name: /trend/i })).toBeNull();
  });

  // ── Trend Chip ───────────────────────────────────────────────────────────
  it('renders positive trend chip with correct label', () => {
    render(wrap(<StatCard {...baseProps} trend={{ value: 12, label: "vs last month" }} />));
    expect(screen.getByText(/\+12%/)).toBeInTheDocument();
    expect(screen.getByText(/vs last month/i)).toBeInTheDocument();
  });

  it('renders negative trend chip for negative trend', () => {
    render(wrap(<StatCard {...baseProps} trend={{ value: -5, label: "vs last month" }} />));
    expect(screen.getByText(/-5%/)).toBeInTheDocument();
  });

  it('shows TrendingUp icon for positive trend', () => {
    render(wrap(<StatCard {...baseProps} trend={{ value: 8, label: "this week" }} />));
    const chip = screen.getByTestId('trend-chip');
    expect(chip).toBeInTheDocument();
  });

  it('shows TrendingDown icon for negative trend', () => {
    render(wrap(<StatCard {...baseProps} trend={{ value: -3, label: "this week" }} />));
    const chip = screen.getByTestId('trend-chip');
    expect(chip).toBeInTheDocument();
  });

  // ── Edge Cases ───────────────────────────────────────────────────────────
  it('handles zero trend value', () => {
    expect(() =>
      render(wrap(<StatCard {...baseProps} trend={{ value: 0, label: "no change" }} />))
    ).not.toThrow();
  });

  it('handles very large numbers', () => {
    render(wrap(<StatCard {...baseProps} value="1,000,000" />));
    expect(screen.getByText('1,000,000')).toBeInTheDocument();
  });

  it('handles Kannada/Unicode title text', () => {
    render(wrap(<StatCard {...baseProps} title="ಒಟ್ಟು ರೈತರು" />));
    expect(screen.getByText('ಒಟ್ಟು ರೈತರು')).toBeInTheDocument();
  });

  // ── Accessibility ────────────────────────────────────────────────────────
  it('card is accessible as a region', () => {
    render(wrap(<StatCard {...baseProps} />));
    expect(screen.getByText('Total Farmers')).toBeVisible();
  });
});
