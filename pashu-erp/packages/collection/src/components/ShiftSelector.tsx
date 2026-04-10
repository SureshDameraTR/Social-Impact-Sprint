import { ToggleButtonGroup, ToggleButton, Typography, Box } from "@mui/material";
import WbSunnyIcon from "@mui/icons-material/WbSunny";
import NightsStayIcon from "@mui/icons-material/NightsStay";
import type { Shift } from "../types";

interface ShiftSelectorProps {
  value: Shift;
  onChange: (shift: Shift) => void;
}

export default function ShiftSelector({ value, onChange }: ShiftSelectorProps) {
  return (
    <Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
        Shift
      </Typography>
      <ToggleButtonGroup
        value={value}
        exclusive
        onChange={(_, v) => { if (v) onChange(v); }}
        fullWidth
      >
        <ToggleButton value="morning" sx={{ py: 1.5 }}>
          <WbSunnyIcon sx={{ mr: 1 }} /> Morning
        </ToggleButton>
        <ToggleButton value="evening" sx={{ py: 1.5 }}>
          <NightsStayIcon sx={{ mr: 1 }} /> Evening
        </ToggleButton>
      </ToggleButtonGroup>
    </Box>
  );
}
