"use client";

import { Chip } from "@mui/material";

const speciesEmoji: Record<string, string> = {
  cattle: "\uD83D\uDC04",
  cow: "\uD83D\uDC04",
  buffalo: "\uD83D\uDC03",
  goat: "\uD83D\uDC10",
  sheep: "\uD83D\uDC11",
  poultry: "\uD83D\uDC14",
  chicken: "\uD83D\uDC14",
  pig: "\uD83D\uDC16",
};

interface SpeciesChipProps {
  species: string;
}

export default function SpeciesChip({ species }: SpeciesChipProps) {
  const emoji = speciesEmoji[species.toLowerCase()] || "\uD83D\uDC3E";
  return (
    <Chip
      label={`${emoji} ${species}`}
      size="small"
      variant="outlined"
      sx={{ fontWeight: 500 }}
    />
  );
}
