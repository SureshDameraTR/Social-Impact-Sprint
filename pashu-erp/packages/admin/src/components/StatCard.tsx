"use client";

import { Card, CardContent, Typography, Box, SvgIconProps } from "@mui/material";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";

interface StatCardProps {
  icon: React.ReactElement<SvgIconProps>;
  title: string;
  value: string | number;
  color: string;
  trend?: { value: number; label: string };
}

export default function StatCard({ icon, title, value, color, trend }: StatCardProps) {
  return (
    <Card
      sx={{
        height: "100%",
        borderLeft: `4px solid ${color}`,
        transition: "box-shadow 0.2s",
        "&:hover": { boxShadow: 4 },
      }}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" fontWeight={700}>
              {value}
            </Typography>
            {trend && (
              <Box display="flex" alignItems="center" mt={0.5}>
                {trend.value >= 0 ? (
                  <TrendingUpIcon sx={{ fontSize: 16, color: "success.main", mr: 0.5 }} />
                ) : (
                  <TrendingDownIcon sx={{ fontSize: 16, color: "error.main", mr: 0.5 }} />
                )}
                <Typography
                  variant="caption"
                  color={trend.value >= 0 ? "success.main" : "error.main"}
                >
                  {trend.value >= 0 ? "+" : ""}
                  {trend.value}% {trend.label}
                </Typography>
              </Box>
            )}
          </Box>
          <Box
            sx={{
              backgroundColor: `${color}15`,
              borderRadius: 2,
              p: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
