"use client";

import React from "react";
import { Chip } from "@mui/material";
import { colors } from "@/theme/theme";

type RiskLevel = "critical" | "high" | "medium" | "low";

const riskConfig: Record<RiskLevel, { bg: string; color: string; label: string }> = {
  critical: { bg: colors.errorLight, color: colors.accentRed, label: 'Critical' },
  high: { bg: colors.warningLight, color: colors.accentAmber, label: 'High' },
  medium: { bg: colors.infoLight, color: colors.accentBlue, label: 'Medium' },
  low: { bg: colors.successLight, color: colors.accentGreen, label: 'Low' },
};

interface RiskBadgeProps {
  level: RiskLevel | string;
  size?: "small" | "medium";
}

function RiskBadgeInner({ level, size = "small" }: RiskBadgeProps) {
  const config = riskConfig[level as RiskLevel] || { bg: '#f0f0f0', color: '#666', label: level };
  return (
    <Chip
      label={config.label}
      size={size}
      sx={{
        fontWeight: 600,
        textTransform: "capitalize",
        bgcolor: config.bg,
        color: config.color,
        border: 'none',
        fontSize: '11.5px',
      }}
    />
  );
}

const RiskBadge = React.memo(RiskBadgeInner);
export default RiskBadge;
