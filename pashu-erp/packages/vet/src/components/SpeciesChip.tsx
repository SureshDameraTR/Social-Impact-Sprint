import { Chip } from "@mui/material";

const SPECIES_COLORS: Record<string, { bg: string; text: string }> = {
  cattle: { bg: "#e8f5e9", text: "#2e7d32" },
  buffalo: { bg: "#e3f2fd", text: "#1565c0" },
  goat: { bg: "#fff3e0", text: "#e65100" },
  sheep: { bg: "#f3e5f5", text: "#7b1fa2" },
  poultry: { bg: "#fff8e1", text: "#f57f17" },
};

export default function SpeciesChip({ species }: { species: string }) {
  const key = species.toLowerCase();
  const { bg, text } = SPECIES_COLORS[key] || { bg: "#f5f5f5", text: "#616161" };

  return (
    <Chip
      label={species}
      size="small"
      sx={{ bgcolor: bg, color: text, fontWeight: 600, fontSize: "11px" }}
    />
  );
}
