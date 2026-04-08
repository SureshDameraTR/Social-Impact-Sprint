"use client";

import { Chip } from "@mui/material";

type RiskLevel = "critical" | "high" | "medium" | "low";

const riskConfig: Record<RiskLevel, { color: "error" | "warning" | "info" | "success"; label: string }> = {
  critical: { color: "error", label: "Critical" },
  high: { color: "warning", label: "High" },
  medium: { color: "info", label: "Medium" },
  low: { color: "success", label: "Low" },
};

interface RiskBadgeProps {
  level: RiskLevel | string;
  size?: "small" | "medium";
}

export default function RiskBadge({ level, size = "small" }: RiskBadgeProps) {
  const config = riskConfig[level as RiskLevel] || { color: "default" as const, label: level };
  return (
    <Chip
      label={config.label}
      color={config.color}
      size={size}
      variant="filled"
      sx={{ fontWeight: 600, textTransform: "capitalize" }}
    />
  );
}
