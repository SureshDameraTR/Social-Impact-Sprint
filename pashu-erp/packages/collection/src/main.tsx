import React from "react";
import ReactDOM from "react-dom/client";
import { ThemeProvider, CssBaseline } from "@mui/material";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { collectionTheme } from "./theme";
import { AuthProvider } from "./hooks/useAuth";
import { CentreProvider } from "./hooks/useCentre";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ThemeProvider theme={collectionTheme}>
      <CssBaseline />
      <BrowserRouter>
        <AuthProvider>
          <CentreProvider>
            <App />
          </CentreProvider>
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  </React.StrictMode>
);
