import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Enroll from "./pages/Enroll";
import Receipt from "./pages/Receipt";
import AuthGuard from "./components/AuthGuard";

function Placeholder({ name }: { name: string }) {
  return <div style={{ padding: 32 }}>{name} — coming soon</div>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/intake" element={<AuthGuard><Placeholder name="Intake" /></AuthGuard>} />
      <Route path="/intake/receipt/:id" element={<AuthGuard><Receipt /></AuthGuard>} />
      <Route path="/enroll" element={<AuthGuard><Enroll /></AuthGuard>} />
      <Route path="/dashboard" element={<AuthGuard><Placeholder name="Dashboard" /></AuthGuard>} />
      <Route path="/settlements" element={<AuthGuard><Placeholder name="Settlements" /></AuthGuard>} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
