import { useState, useEffect, useCallback } from "react";
import {
  Box,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  ToggleButton,
  ToggleButtonGroup,
} from "@mui/material";
import { getFarmerSettlements } from "../api/milk";
import { useCentre } from "../hooks/useCentre";
import { inrFormatter } from "../types";

interface FarmerSettlement {
  farmer_user_id: string;
  total_liters: number;
  total_amount_inr: number;
  deliveries: number;
  avg_fat_pct: number;
  avg_snf_pct: number;
}

interface SettlementsResponse {
  center_id: string;
  period_days: number;
  settlements: FarmerSettlement[];
  total_farmers: number;
  total_payout_inr: number;
}

const PERIOD_OPTIONS = [15, 30, 45] as const;

export default function Settlements() {
  const { centreId } = useCentre();
  const [period, setPeriod] = useState<number>(15);
  const [data, setData] = useState<SettlementsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSettlements = useCallback(async () => {
    if (!centreId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await getFarmerSettlements(centreId, period);
      setData(res.data);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to load settlements";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [centreId, period]);

  useEffect(() => {
    setData(null);
    fetchSettlements();
  }, [fetchSettlements]);

  const handlePeriodChange = (
    _event: React.MouseEvent<HTMLElement>,
    newPeriod: number | null,
  ) => {
    if (newPeriod !== null) {
      setPeriod(newPeriod);
    }
  };

  return (
    <Box p={3}>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Farmer Settlements
      </Typography>

      <Box mb={3}>
        <ToggleButtonGroup
          value={period}
          exclusive
          onChange={handlePeriodChange}
          size="small"
        >
          {PERIOD_OPTIONS.map((days) => (
            <ToggleButton key={days} value={days}>
              {days} days
            </ToggleButton>
          ))}
        </ToggleButtonGroup>
      </Box>

      {loading && (
        <Box display="flex" justifyContent="center" py={6} role="status" aria-label="Loading settlements">
          <CircularProgress />
        </Box>
      )}

      {error && <Alert severity="error">{error}</Alert>}

      {!loading && !error && data && (
        <>
          <TableContainer component={Paper}>
            <Table size="small" aria-label="Farmer settlements">
              <TableHead>
                <TableRow>
                  <TableCell>#</TableCell>
                  <TableCell>Farmer ID</TableCell>
                  <TableCell align="right">Deliveries</TableCell>
                  <TableCell align="right">Total Liters</TableCell>
                  <TableCell align="right">Avg Fat%</TableCell>
                  <TableCell align="right">Avg SNF%</TableCell>
                  <TableCell align="right">Total Payout</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.settlements.map((s, idx) => (
                  <TableRow key={s.farmer_user_id}>
                    <TableCell>{idx + 1}</TableCell>
                    <TableCell>{s.farmer_user_id.slice(0, 8)}</TableCell>
                    <TableCell align="right">{s.deliveries}</TableCell>
                    <TableCell align="right">{Number(s.total_liters).toFixed(1)}</TableCell>
                    <TableCell align="right">{Number(s.avg_fat_pct).toFixed(1)}</TableCell>
                    <TableCell align="right">{Number(s.avg_snf_pct).toFixed(1)}</TableCell>
                    <TableCell align="right">
                      {inrFormatter.format(s.total_amount_inr)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            mt={2}
            px={1}
          >
            <Typography variant="body2" color="text.secondary">
              Total Farmers: {data.total_farmers}
            </Typography>
            <Typography variant="body1" fontWeight={700}>
              Total Payout: {inrFormatter.format(data.total_payout_inr)}
            </Typography>
          </Box>
        </>
      )}
    </Box>
  );
}
