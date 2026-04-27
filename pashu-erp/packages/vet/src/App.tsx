import { Routes, Route, Navigate } from "react-router-dom";
import { Box } from "@mui/material";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Cases from "./pages/Cases";
import CaseDetail from "./pages/CaseDetail";
import Alerts from "./pages/Alerts";
import AuthGuard from "./components/AuthGuard";
import NavBar from "./components/NavBar";

function ProtectedLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <Box
        component="a"
        href="#main-content"
        sx={{
          position: 'absolute',
          left: '-9999px',
          top: 'auto',
          zIndex: 9999,
          bgcolor: '#1565c0',
          color: '#fff',
          p: '8px 16px',
          textDecoration: 'none',
          fontWeight: 600,
          fontSize: 14,
          '&:focus': { position: 'static', display: 'block' },
        }}
      >
        Skip to main content
      </Box>
      <NavBar />
      <Box component="main" id="main-content">{children}</Box>
    </AuthGuard>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={<ProtectedLayout><Dashboard /></ProtectedLayout>} />
      <Route path="/cases" element={<ProtectedLayout><Cases /></ProtectedLayout>} />
      <Route path="/cases/:id" element={<ProtectedLayout><CaseDetail /></ProtectedLayout>} />
      <Route path="/alerts" element={<ProtectedLayout><Alerts /></ProtectedLayout>} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
