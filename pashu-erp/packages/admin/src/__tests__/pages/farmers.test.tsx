import React from 'react';
import { render, screen, fireEvent, within } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { adminTheme } from '../../theme/theme';

// NOTE: Refine provider is mocked — test the UI behavior only
jest.mock('@refinedev/core', () => ({
  useList: () => ({ data: { data: mockFarmers }, isLoading: false }),
  useNavigation: () => ({ show: jest.fn(), create: jest.fn() }),
}));

const mockFarmers = [
  { id: '1', name: 'Ravi Kumar', phone: '9876543210', district: 'Mysuru', village: 'Bannur', animalCount: 4, createdAt: '2024-01-15' },
  { id: '2', name: 'Leela Devi', phone: '9123456780', district: 'Mandya', village: 'Maddur', animalCount: 2, createdAt: '2024-03-01' },
  { id: '3', name: 'Suresh Gowda', phone: '9000000001', district: 'Hassan', village: 'Sakleshpur', animalCount: 7, createdAt: '2023-11-20' },
];

// Dynamic import of the page
// eslint-disable-next-line @typescript-eslint/no-var-requires
const FarmersPage = require('../../app/farmers/page').default;

const wrap = (ui: React.ReactElement) => (
  <ThemeProvider theme={adminTheme}>{ui}</ThemeProvider>
);

describe('Farmers Page', () => {
  // ── Rendering ────────────────────────────────────────────────────────────
  it('renders the page title', () => {
    render(wrap(<FarmersPage />));
    expect(screen.getByText(/Farmers/i)).toBeInTheDocument();
  });

  it('renders all farmers from data', () => {
    render(wrap(<FarmersPage />));
    expect(screen.getByText('Ravi Kumar')).toBeInTheDocument();
    expect(screen.getByText('Leela Devi')).toBeInTheDocument();
    expect(screen.getByText('Suresh Gowda')).toBeInTheDocument();
  });

  it('renders the search input', () => {
    render(wrap(<FarmersPage />));
    expect(screen.getByPlaceholderText(/Search by name or phone/i)).toBeInTheDocument();
  });

  // ── Search Filtering ──────────────────────────────────────────────────────
  it('filters rows when typing in search box', () => {
    render(wrap(<FarmersPage />));
    const input = screen.getByPlaceholderText(/Search by name or phone/i);
    fireEvent.change(input, { target: { value: 'Leela' } });
    expect(screen.getByText('Leela Devi')).toBeInTheDocument();
    expect(screen.queryByText('Ravi Kumar')).toBeNull();
  });

  it('shows all rows when search is cleared', () => {
    render(wrap(<FarmersPage />));
    const input = screen.getByPlaceholderText(/Search by name or phone/i);
    fireEvent.change(input, { target: { value: 'Ravi' } });
    fireEvent.change(input, { target: { value: '' } });
    expect(screen.getByText('Ravi Kumar')).toBeInTheDocument();
    expect(screen.getByText('Leela Devi')).toBeInTheDocument();
  });

  it('is case-insensitive in search', () => {
    render(wrap(<FarmersPage />));
    const input = screen.getByPlaceholderText(/Search by name or phone/i);
    fireEvent.change(input, { target: { value: 'ravi' } });
    expect(screen.getByText('Ravi Kumar')).toBeInTheDocument();
  });

  it('shows empty state when no results match', () => {
    render(wrap(<FarmersPage />));
    const input = screen.getByPlaceholderText(/Search by name or phone/i);
    fireEvent.change(input, { target: { value: 'xyznotexist' } });
    expect(screen.queryByText('Ravi Kumar')).toBeNull();
    expect(screen.queryByText('Leela Devi')).toBeNull();
  });

  // ── Table Structure ───────────────────────────────────────────────────────
  it('renders correct column headers', () => {
    render(wrap(<FarmersPage />));
    expect(screen.getByText(/Name/i)).toBeInTheDocument();
    expect(screen.getByText(/Phone/i)).toBeInTheDocument();
    expect(screen.getByText(/District/i)).toBeInTheDocument();
    expect(screen.getByText(/Animals/i)).toBeInTheDocument();
  });

  // ── Pagination ────────────────────────────────────────────────────────────
  it('renders pagination controls', () => {
    render(wrap(<FarmersPage />));
    expect(screen.getByRole('navigation', { name: /pagination/i })).toBeInTheDocument();
  });

  // ── Accessibility ─────────────────────────────────────────────────────────
  it('table has accessible role', () => {
    render(wrap(<FarmersPage />));
    expect(screen.getByRole('table')).toBeInTheDocument();
  });
});
