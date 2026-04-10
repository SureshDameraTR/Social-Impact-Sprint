import { Routes, Route, Navigate } from "react-router-dom";

function Placeholder({ name }: { name: string }) {
  return <div style={{ padding: 32 }}>{name} — coming soon</div>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Placeholder name="Login" />} />
      <Route path="/intake" element={<Placeholder name="Intake" />} />
      <Route path="/intake/receipt/:id" element={<Placeholder name="Receipt" />} />
      <Route path="/enroll" element={<Placeholder name="Enroll" />} />
      <Route path="/dashboard" element={<Placeholder name="Dashboard" />} />
      <Route path="/settlements" element={<Placeholder name="Settlements" />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
