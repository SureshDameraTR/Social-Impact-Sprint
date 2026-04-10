import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
} from "@mui/material";
import FarmerSearch from "../components/FarmerSearch";
import ShiftSelector from "../components/ShiftSelector";
import RatePreview from "../components/RatePreview";
import { receiveMilk } from "../api/milk";
import { useCentre } from "../hooks/useCentre";

interface Farmer {
  id: string;
  name: string;
  phone: string;
  aadhaar_last4: string | null;
  village_code: string | null;
  district: string | null;
}

function getDefaultShift(): "morning" | "evening" {
  return new Date().getHours() < 12 ? "morning" : "evening";
}

export default function Intake() {
  const navigate = useNavigate();
  const { centreId } = useCentre();

  const [farmer, setFarmer] = useState<Farmer | null>(null);
  const [quantity, setQuantity] = useState("");
  const [fatPct, setFatPct] = useState("");
  const [snfPct, setSnfPct] = useState("");
  const [shift, setShift] = useState<"morning" | "evening">(getDefaultShift());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const qtyNum = parseFloat(quantity) || null;
  const fatNum = parseFloat(fatPct) || null;
  const snfNum = parseFloat(snfPct) || null;

  const canSubmit = farmer && qtyNum && qtyNum > 0 && fatNum && fatNum >= 1 && fatNum <= 12 && snfNum && snfNum >= 6 && snfNum <= 12 && centreId;

  const handleSubmit = async () => {
    if (!canSubmit || !farmer || !centreId) return;
    setLoading(true);
    setError("");
    try {
      const { data } = await receiveMilk({
        center_id: centreId,
        farmer_user_id: farmer.id,
        quantity_liters: qtyNum!,
        fat_pct: fatNum!,
        snf_pct: snfNum!,
        shift,
      });
      navigate(`/intake/receipt/${data.id}`, {
        state: {
          ...data,
          farmer_name: farmer.name,
          farmer_phone: farmer.phone,
        },
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to submit";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  if (!centreId) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">
          No collection centre selected. Please contact your administrator.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 600, mx: "auto", p: 2 }}>
      <Typography variant="h5" fontWeight={700} sx={{ mb: 2 }}>
        Milk Intake
      </Typography>

      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
            Farmer
          </Typography>
          <FarmerSearch onSelect={setFarmer} selected={farmer} />
        </CardContent>
      </Card>

      {farmer && (
        <>
          <Card sx={{ mb: 2 }}>
            <CardContent sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
              <Typography variant="subtitle2" color="text.secondary">
                Milk Details
              </Typography>
              <TextField
                label="Quantity (liters)"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                inputProps={{ inputMode: "decimal" }}
                fullWidth
                autoFocus
              />
              <Box sx={{ display: "flex", gap: 2 }}>
                <TextField
                  label="Fat %"
                  value={fatPct}
                  onChange={(e) => setFatPct(e.target.value)}
                  inputProps={{ inputMode: "decimal" }}
                  helperText="1.0 – 12.0"
                  fullWidth
                />
                <TextField
                  label="SNF %"
                  value={snfPct}
                  onChange={(e) => setSnfPct(e.target.value)}
                  inputProps={{ inputMode: "decimal" }}
                  helperText="6.0 – 12.0"
                  fullWidth
                />
              </Box>
              <ShiftSelector value={shift} onChange={setShift} />
            </CardContent>
          </Card>

          <RatePreview fatPct={fatNum} snfPct={snfNum} quantity={qtyNum} />

          {error && (
            <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError("")}>
              {error}
            </Alert>
          )}

          <Button
            variant="contained"
            size="large"
            fullWidth
            onClick={handleSubmit}
            disabled={!canSubmit || loading}
            sx={{ mt: 2, py: 1.5, fontSize: 16, fontWeight: 700 }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : "Submit Milk Record"}
          </Button>
        </>
      )}
    </Box>
  );
}
