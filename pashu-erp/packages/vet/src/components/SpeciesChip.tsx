import { Chip } from "@mui/material";
import { vetTheme } from "../theme";

const palette = vetTheme.palette;

const SPECIES_COLORS: Record<string, { bg: string; text: string }> = {
  cattle: { bg: palette.success.light, text: palette.success.main },
  buffalo: { bg: palette.primary.light, text: palette.primary.main },
  goat: { bg: palette.warning.light, text: palette.warning.main },
  sheep: { bg: "#f3e5f5", text: "#7b1fa2" },
  poultry: { bg: "#fff8e1", text: "#f57f17" },
};

export default function SpeciesChip({ species }: { species: string }) {
  const key = species.toLowerCase();
  const { bg, text } = SPECIES_COLORS[key] || { bg: palette.background.default, text: palette.text.secondary };

  return (
    <Chip
      label={species}
      size="small"
      sx={{ bgcolor: bg, color: text, fontWeight: 600, fontSize: "11px" }}
    />
  );
}
