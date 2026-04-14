import { createTheme } from "@mui/material/styles";

export const vetTheme = createTheme({
  palette: {
    primary: { main: "#1565c0", light: "#e3f2fd", dark: "#0d47a1" },
    secondary: { main: "#0d6b58", light: "#e8f5f1" },
    error: { main: "#c62828", light: "#ffebee" },
    warning: { main: "#e65100", light: "#fff3e0" },
    success: { main: "#2e7d32", light: "#e8f5e9" },
    info: { main: "#0277bd", light: "#e1f5fe" },
    background: { default: "#f5f7fa", paper: "#ffffff" },
    text: { primary: "#1a2332", secondary: "#5f6d7e" },
  },
  typography: {
    fontFamily: '"IBM Plex Sans", system-ui, -apple-system, sans-serif',
  },
  shape: { borderRadius: 10 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 8, textTransform: "none" as const, fontWeight: 600 },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: { borderRadius: 14, boxShadow: "0 1px 3px rgba(0,0,0,0.06)" },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: { "& .MuiOutlinedInput-root": { borderRadius: 8 } },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { borderRadius: 6, fontWeight: 600, fontSize: "11px" },
      },
    },
  },
});

/** Reusable color tokens */
export const colors = {
  emergency: { bg: "#ffebee", text: "#c62828" },
  urgent: { bg: "#fff3e0", text: "#e65100" },
  routine: { bg: "#f5f5f5", text: "#616161" },
  pending: { bg: "#fff3e0", text: "#e65100" },
  in_review: { bg: "#e3f2fd", text: "#1565c0" },
  diagnosed: { bg: "#e8f5e9", text: "#2e7d32" },
  closed: { bg: "#f5f5f5", text: "#616161" },
  photo: { bg: "#e3f2fd", text: "#1565c0" },
  walk_in: { bg: "#e8f5e9", text: "#2e7d32" },
  referral: { bg: "#fff3e0", text: "#e65100" },
};
