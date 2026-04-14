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
      <NavBar />
      <Box component="main">{children}</Box>
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
