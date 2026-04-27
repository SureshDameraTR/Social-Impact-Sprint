"use client";

import React from "react";
import { Chip } from "@mui/material";
import { colors } from "@/theme/theme";

const speciesConfig: Record<string, { emoji: string; bg: string; color: string }> = {
  cattle: { emoji: "\uD83D\uDC04", bg: colors.primaryLight, color: colors.primary },
  cow: { emoji: "\uD83D\uDC04", bg: colors.primaryLight, color: colors.primary },
  buffalo: { emoji: "\uD83D\uDC03", bg: colors.infoLight, color: colors.secondary },
  goat: { emoji: "\uD83D\uDC10", bg: colors.warningLight, color: colors.accentAmber },
  sheep: { emoji: "\uD83D\uDC11", bg: colors.errorLight, color: colors.accentRed },
  poultry: { emoji: "\uD83D\uDC14", bg: colors.infoLight, color: colors.accentBlue },
  chicken: { emoji: "\uD83D\uDC14", bg: colors.infoLight, color: colors.accentBlue },
  pig: { emoji: "\uD83D\uDC16", bg: colors.successLight, color: colors.accentGreen },
};

interface SpeciesChipProps {
  species: string;
}

function SpeciesChipInner({ species }: SpeciesChipProps) {
  const config = speciesConfig[species.toLowerCase()] || {
    emoji: "\uD83D\uDC3E",
    bg: colors.primaryLight,
    color: colors.primary,
  };
  return (
    <Chip
      label={`${config.emoji} ${species}`}
      size="small"
      sx={{
        fontWeight: 500,
        bgcolor: config.bg,
        color: config.color,
        border: 'none',
        fontSize: '12px',
      }}
    />
  );
}

const SpeciesChip = React.memo(SpeciesChipInner);
export default SpeciesChip;
