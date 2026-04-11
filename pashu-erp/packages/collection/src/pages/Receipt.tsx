import { useLocation, useNavigate, Link } from "react-router-dom";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Divider,
  Alert,
} from "@mui/material";
import { useCentre } from "../hooks/useCentre";
import "../utils/print.css";

interface ReceiptState {
  id: string;
  center_id: string;
  farmer_user_id: string;
  farmer_name: string;
  farmer_phone: string;
  quantity_liters: number;
  fat_pct: number;
  snf_pct: number;
  rate_per_liter: number;
  total_amount: number;
  shift: string;
  collected_at: string;
}

function formatDateTime(iso: string) {
  const d = new Date(iso);
  const date = d.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    timeZone: "Asia/Kolkata",
  });
  const time = d.toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Asia/Kolkata",
  });
  return { date, time };
}

export default function Receipt() {
  const location = useLocation();
  const navigate = useNavigate();
  const { centreName } = useCentre();

  const state = location.state as ReceiptState | null;

  if (!state) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">
          No receipt data available. Please submit a milk record first.
        </Alert>
        <Link to="/intake" style={{ marginTop: 16, display: "inline-block" }}>
          Go to Intake
        </Link>
      </Box>
    );
  }

  const { date, time } = formatDateTime(state.collected_at);
  const receiptNumber = state.id.substring(0, 8).toUpperCase();

  return (
    <Box sx={{ maxWidth: 480, mx: "auto", p: 2 }}>
      <div id="receipt-content">
        <Card>
          <CardContent>
            {/* Header */}
            <Typography variant="h6" fontWeight={700} textAlign="center">
              {centreName ?? "Collection Centre"}
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              textAlign="center"
              sx={{ mb: 2 }}
            >
              Receipt #{receiptNumber}
            </Typography>

            <Divider sx={{ mb: 2 }} />

            {/* Date / Time / Shift */}
            <Row label="Date" value={date} />
            <Row label="Time" value={time} />
            <Row label="Shift" value={state.shift} />

            <Divider sx={{ my: 1.5 }} />

            {/* Farmer */}
            <Row label="Farmer" value={state.farmer_name} />
            <Row label="Phone" value={state.farmer_phone} />

            <Divider sx={{ my: 1.5 }} />

            {/* Milk Details */}
            <Row label="Quantity" value={`${state.quantity_liters} L`} />
            <Row label="Fat %" value={`${state.fat_pct}%`} />
            <Row label="SNF %" value={`${state.snf_pct}%`} />

            <Divider sx={{ my: 1.5 }} />

            {/* Payment */}
            <Row
              label="Rate / Liter"
              value={`\u20B9${state.rate_per_liter.toFixed(2)}`}
            />
            <Row
              label="Total Amount"
              value={`\u20B9${state.total_amount.toFixed(2)}`}
              bold
            />
          </CardContent>
        </Card>
      </div>

      {/* Actions */}
      <Box sx={{ display: "flex", gap: 2, mt: 3 }}>
        <Button
          variant="outlined"
          fullWidth
          size="large"
          onClick={() => window.print()}
        >
          Print Receipt
        </Button>
        <Button
          variant="contained"
          fullWidth
          size="large"
          onClick={() => navigate("/intake")}
        >
          Next Farmer
        </Button>
      </Box>
    </Box>
  );
}

function Row({
  label,
  value,
  bold,
}: {
  label: string;
  value: string;
  bold?: boolean;
}) {
  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "space-between",
        py: 0.4,
      }}
    >
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2" fontWeight={bold ? 700 : 400}>
        {value}
      </Typography>
    </Box>
  );
}
