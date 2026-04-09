import { createTheme } from '@mui/material/styles';

export const adminTheme = createTheme({
  palette: {
    primary: { main: '#0d6b58', light: '#e8f5f1', dark: '#094d3f' },
    secondary: { main: '#1e3a5f', light: '#e8eef6' },
    error: { main: '#c0392b', light: '#fdeaea' },
    warning: { main: '#d97706', light: '#fef3c7' },
    success: { main: '#16a34a', light: '#dcfce7' },
    info: { main: '#0369a1', light: '#e0f2fe' },
    background: { default: '#f0f4f3', paper: '#ffffff' },
    text: { primary: '#1a2e2a', secondary: '#5f7a74' },
  },
  typography: {
    fontFamily: '"IBM Plex Sans", system-ui, -apple-system, sans-serif',
    h4: { fontWeight: 700, letterSpacing: '-0.02em' },
    h5: { fontWeight: 700 },
    h6: { fontWeight: 600, fontSize: '14px' },
    body1: { fontSize: '13.5px' },
    body2: { fontSize: '12px', color: '#5f7a74' },
    caption: {
      fontSize: '11px',
      letterSpacing: '0.05em',
      textTransform: 'uppercase' as const,
      fontWeight: 600,
    },
  },
  shape: { borderRadius: 10 },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 14,
          boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
          '&:hover': { boxShadow: '0 4px 12px rgba(0,0,0,0.08)' },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 14,
          boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
        },
      },
    },
    MuiTableHead: {
      styleOverrides: {
        root: {
          '& .MuiTableCell-head': {
            fontSize: '11.5px',
            fontWeight: 600,
            textTransform: 'uppercase' as const,
            letterSpacing: '0.05em',
            color: '#5f7a74',
            borderBottom: '2px solid rgba(0,0,0,0.08)',
            padding: '12px 18px',
            backgroundColor: '#f7faf9',
          },
        },
      },
    },
    MuiTableBody: {
      styleOverrides: {
        root: {
          '& .MuiTableCell-body': {
            padding: '14px 18px',
            fontSize: '13.5px',
            borderBottom: '1px solid rgba(0,0,0,0.08)',
          },
        },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        root: {
          '&:hover': { backgroundColor: 'rgba(13,107,88,0.08)' },
          transition: 'background-color 0.15s ease',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { borderRadius: 10, fontWeight: 500, fontSize: '12px' },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none' as const,
          fontWeight: 600,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            fontSize: '13px',
          },
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          height: 6,
          backgroundColor: 'rgba(0,0,0,0.06)',
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 10,
        },
      },
    },
  },
});

/* Re-export palette tokens for easy use in components */
export const colors = {
  bg: '#f0f4f3',
  surface: '#ffffff',
  surfaceAlt: '#f7faf9',
  border: 'rgba(0,0,0,0.08)',
  text: '#1a2e2a',
  textDim: '#5f7a74',
  textLight: '#8fa5a0',
  primary: '#0d6b58',
  primaryLight: '#e8f5f1',
  secondary: '#1e3a5f',
  accentAmber: '#d97706',
  accentRed: '#c0392b',
  accentGreen: '#16a34a',
  accentBlue: '#0369a1',
  successLight: '#dcfce7',
  errorLight: '#fdeaea',
  warningLight: '#fef3c7',
  infoLight: '#e0f2fe',
  sidebarBg: '#0f2b24',
  sidebarText: '#c8ddd8',
  sidebarActive: '#16a085',
};

/* Shared typography & chart constants */
export const monoFont = '"IBM Plex Mono", "SF Mono", Consolas, monospace';

export const sxCodeCell = {
  fontFamily: monoFont,
  fontSize: '12px',
  color: colors.textDim,
} as const;

export const sxNameCell = {
  fontWeight: 500,
  color: colors.text,
} as const;

export const tooltipStyle = {
  borderRadius: 8,
  border: 'none',
  boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
  fontSize: 12,
} as const;

export const axisTickStyle = { fontSize: 11, fill: colors.textDim } as const;

export const gridStroke = 'rgba(0,0,0,0.06)';
