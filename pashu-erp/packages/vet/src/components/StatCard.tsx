import { Card, CardContent, Typography, Box } from "@mui/material";
import type { SxProps, Theme } from "@mui/material";

interface StatCardProps {
  label: string;
  value: number | string;
  icon: React.ReactNode;
  color?: string;
  sx?: SxProps<Theme>;
}

export default function StatCard({ label, value, icon, color = "primary.main", sx }: StatCardProps) {
  return (
    <Card sx={{ height: "100%", ...sx }}>
      <CardContent sx={{ display: "flex", alignItems: "center", gap: 2, py: 2.5 }}>
        <Box
          sx={{
            width: 48,
            height: 48,
            borderRadius: 2,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            bgcolor: `${color}15`,
            color,
            flexShrink: 0,
          }}
        >
          {icon}
        </Box>
        <Box>
          <Typography variant="h5" fontWeight={700} sx={{ color }}>
            {value}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {label}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}
