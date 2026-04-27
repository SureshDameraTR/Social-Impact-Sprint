"use client";

import { useList } from "@refinedev/core";
import { Box, Typography, Paper, CircularProgress, Alert } from "@mui/material";
import GISMap, { MapPoint } from "@/components/GISMap";
import { colors } from "@/theme/theme";

export default function MapPage() {
  // API may return extra fields (lon, risk_score, village_code, disease_name)
  interface RawMapPoint extends Omit<MapPoint, 'type'> {
    type?: string;
    lon?: number;
    risk_score?: number;
    village_code?: string;
    disease_name?: string;
  }

  const { data, isLoading, isError } = useList<RawMapPoint>({ resource: "map/points" });

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 8 }} role="status" aria-label="Loading map data"><CircularProgress /></Box>;
  if (isError) return <Box sx={{ p: 4 }}><Alert severity="error">Failed to load data from server.</Alert></Box>;

  // Map API response format to GISMap MapPoint format
  const rawPoints = data?.data ?? [];
  const allPoints: MapPoint[] = rawPoints
    .filter((p) => p.lat != null && (p.lng != null || p.lon != null))
    .map((p, idx) => ({
      id: String(p.id ?? p.village_code ?? `point-${p.lat}-${p.lng}-${idx}`),
      lat: Number(p.lat),
      lng: Number(p.lng ?? p.lon),
      label: String(p.label ?? p.disease_name ?? ""),
      details: p.details ? String(p.details) : undefined,
      severity: p.severity ?? (p.risk_score != null ? (p.risk_score >= 0.8 ? "critical" : p.risk_score >= 0.6 ? "high" : "medium") : undefined),
      type: p.type === "health_alert" || p.type === "community_alert" ? "alert" as const
        : p.type === "milk_center" ? "center" as const
        : p.type === "farmer_cluster" ? "farmer" as const
        : undefined,
    }));

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ color: colors.text }}>
        Map View
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={2}>
        Karnataka livestock monitoring -- toggle layers using the control on the top right
      </Typography>

      <Paper sx={{ overflow: "hidden" }}>
        {allPoints.length === 0 ? (
          <Typography color="text.secondary" sx={{ p: 4, textAlign: 'center' }}>No map data available. Ensure the API is running and database is seeded.</Typography>
        ) : (
          <GISMap
            center={[13.0, 76.5]}
            zoom={7}
            points={allPoints}
            height="calc(100vh - 220px)"
            showLayers
          />
        )}
      </Paper>

      {/* Legend */}
      <Paper sx={{ p: 2, mt: 2 }}>
        <Typography sx={{ fontSize: '12px', fontWeight: 600, color: colors.text, mb: 1, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Legend
        </Typography>
        <Box display="flex" gap={3} flexWrap="wrap">
          {[
            { color: colors.accentRed, label: "Critical Alert" },
            { color: colors.accentAmber, label: "High Alert" },
            { color: colors.accentAmber, label: "Medium Alert" },
            { color: colors.accentBlue, label: "Milk Center" },
            { color: colors.accentGreen, label: "Farmer Location" },
          ].map((item) => (
            <Box key={item.label} display="flex" alignItems="center" gap={1}>
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  backgroundColor: item.color,
                }}
              />
              <Typography sx={{ fontSize: '12px', color: colors.textDim }}>
                {item.label}
              </Typography>
            </Box>
          ))}
        </Box>
      </Paper>
    </Box>
  );
}
