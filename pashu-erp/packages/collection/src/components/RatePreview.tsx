import { Box, Typography } from "@mui/material";
import { calculateRate } from "../utils/pricing";

interface RatePreviewProps {
  fatPct: number | null;
  snfPct: number | null;
  quantity: number | null;
}

export default function RatePreview({ fatPct, snfPct, quantity }: RatePreviewProps) {
  const hasValues = fatPct != null && snfPct != null && fatPct > 0 && snfPct > 0;
  const rate = hasValues ? calculateRate(fatPct, snfPct) : null;
  const total = rate != null && quantity != null && quantity > 0 ? Math.round(rate * quantity * 100) / 100 : null;

  return (
    <Box
      sx={{
        p: 2,
        bgcolor: hasValues ? "success.light" : "grey.100",
        borderRadius: 2,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}
    >
      <Box>
        <Typography variant="caption" color="text.secondary">Rate per liter</Typography>
        <Typography variant="h5" fontWeight={700}>
          {rate != null ? `₹${rate.toFixed(2)}` : "—"}
        </Typography>
      </Box>
      <Box sx={{ textAlign: "right" }}>
        <Typography variant="caption" color="text.secondary">Total amount</Typography>
        <Typography variant="h5" fontWeight={700} color="primary">
          {total != null ? `₹${total.toFixed(2)}` : "—"}
        </Typography>
      </Box>
    </Box>
  );
}
