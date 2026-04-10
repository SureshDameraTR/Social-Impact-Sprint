import { Routes, Route, Navigate } from "react-router-dom";
import { Box } from "@mui/material";
import Login from "./pages/Login";
import Intake from "./pages/Intake";
import Receipt from "./pages/Receipt";
import Enroll from "./pages/Enroll";
import Dashboard from "./pages/Dashboard";
import Settlements from "./pages/Settlements";
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
      <Route path="/intake" element={<ProtectedLayout><Intake /></ProtectedLayout>} />
      <Route path="/intake/receipt/:id" element={<ProtectedLayout><Receipt /></ProtectedLayout>} />
      <Route path="/enroll" element={<ProtectedLayout><Enroll /></ProtectedLayout>} />
      <Route path="/dashboard" element={<ProtectedLayout><Dashboard /></ProtectedLayout>} />
      <Route path="/settlements" element={<ProtectedLayout><Settlements /></ProtectedLayout>} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
