import { createTheme } from "@mui/material/styles";

export const collectionTheme = createTheme({
  palette: {
    primary: { main: "#0d6b58", light: "#e8f5f1", dark: "#094d3f" },
    secondary: { main: "#1e3a5f", light: "#e8eef6" },
    error: { main: "#c0392b", light: "#fdeaea" },
    warning: { main: "#d97706", light: "#fef3c7" },
    success: { main: "#16a34a", light: "#dcfce7" },
    info: { main: "#0369a1", light: "#e0f2fe" },
    background: { default: "#f0f4f3", paper: "#ffffff" },
    text: { primary: "#1a2e2a", secondary: "#5f7a74" },
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
        root: {
          "& .MuiOutlinedInput-root": { borderRadius: 8 },
        },
      },
    },
  },
});
