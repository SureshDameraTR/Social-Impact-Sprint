"use client";

import React from "react";
import { Card, CardContent, Typography, Box, Chip, SvgIconProps } from "@mui/material";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import { colors } from "@/theme/theme";

interface StatCardProps {
  icon: React.ReactElement<SvgIconProps>;
  title: string;
  value: string | number;
  color: string;
  trend?: { value: number; label: string };
}

function StatCardInner({ icon, title, value, color, trend }: StatCardProps) {
  const isPositive = trend ? trend.value >= 0 : true;

  return (
    <Card
      sx={{
        height: "100%",
        borderTop: `3px solid ${color}`,
        borderRadius: '14px',
        transition: "all 0.2s ease",
        "&:hover": {
          boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
          transform: 'translateY(-1px)',
        },
      }}
    >
      <CardContent sx={{ p: 2.5, '&:last-child': { pb: 2.5 } }}>
        <Box
          sx={{
            width: 42,
            height: 42,
            borderRadius: '10px',
            bgcolor: `${color}15`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            mb: 1.5,
          }}
          role="img"
          aria-label={`${title} icon`}
        >
          {icon}
        </Box>
        <Typography
          sx={{
            fontSize: '30px',
            fontWeight: 700,
            color: colors.text,
            lineHeight: 1.1,
            letterSpacing: '-0.02em',
          }}
        >
          {value}
        </Typography>
        <Typography
          sx={{
            fontSize: '13px',
            color: colors.textDim,
            fontWeight: 500,
            mt: 0.5,
          }}
        >
          {title}
        </Typography>
        {trend && (
          <Chip
            data-testid="trend-chip"
            size="small"
            icon={
              isPositive ? (
                <TrendingUpIcon sx={{ fontSize: '14px !important' }} aria-label="Trending up" />
              ) : (
                <TrendingDownIcon sx={{ fontSize: '14px !important' }} aria-label="Trending down" />
              )
            }
            label={`${isPositive ? "+" : ""}${trend.value}% ${trend.label}`}
            sx={{
              mt: 1,
              height: 22,
              fontSize: '11px',
              fontWeight: 600,
              bgcolor: isPositive ? colors.successLight : colors.errorLight,
              color: isPositive ? colors.accentGreen : colors.accentRed,
              '& .MuiChip-icon': {
                color: isPositive ? colors.accentGreen : colors.accentRed,
              },
              border: 'none',
            }}
          />
        )}
      </CardContent>
    </Card>
  );
}

const StatCard = React.memo(StatCardInner);
export default StatCard;
