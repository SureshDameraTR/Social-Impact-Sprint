import { Routes, Route, Navigate } from "react-router-dom";
import { Box, Alert } from "@mui/material";
import Login from "./pages/Login";
import Intake from "./pages/Intake";
import Receipt from "./pages/Receipt";
import Enroll from "./pages/Enroll";
import Dashboard from "./pages/Dashboard";
import Settlements from "./pages/Settlements";
import AuthGuard from "./components/AuthGuard";
import NavBar from "./components/NavBar";
import { useCentre } from "./hooks/useCentre";

function CentreGuard({ children }: { children: React.ReactNode }) {
  const { centreId } = useCentre();
  if (!centreId) {
    return (
      <Box p={3}>
        <Alert severity="warning">
          No collection centre selected. Please contact your administrator.
        </Alert>
      </Box>
    );
  }
  return <>{children}</>;
}

function ProtectedLayout({ children, requireCentre = false }: { children: React.ReactNode; requireCentre?: boolean }) {
  return (
    <AuthGuard>
      <NavBar />
      <Box component="main">
        {requireCentre ? <CentreGuard>{children}</CentreGuard> : children}
      </Box>
    </AuthGuard>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/intake" element={<ProtectedLayout requireCentre><Intake /></ProtectedLayout>} />
      <Route path="/intake/receipt/:id" element={<ProtectedLayout><Receipt /></ProtectedLayout>} />
      <Route path="/enroll" element={<ProtectedLayout><Enroll /></ProtectedLayout>} />
      <Route path="/dashboard" element={<ProtectedLayout requireCentre><Dashboard /></ProtectedLayout>} />
      <Route path="/settlements" element={<ProtectedLayout requireCentre><Settlements /></ProtectedLayout>} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
