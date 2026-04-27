import { Box, Paper, Skeleton } from "@mui/material";

/** Loading skeleton for the Map View page. */
export default function MapLoading() {
  return (
    <Box p={3}>
      <Skeleton variant="text" width={160} height={40} sx={{ mb: 0.5 }} />
      <Skeleton variant="text" width={400} height={24} sx={{ mb: 2 }} />

      {/* Map skeleton */}
      <Paper sx={{ overflow: "hidden" }}>
        <Skeleton
          variant="rectangular"
          height="calc(100vh - 280px)"
          sx={{ borderRadius: 0, minHeight: 400 }}
        />
      </Paper>

      {/* Legend skeleton */}
      <Paper sx={{ p: 2, mt: 2 }}>
        <Skeleton variant="text" width={60} height={16} sx={{ mb: 1 }} />
        <Box display="flex" gap={3} flexWrap="wrap">
          {Array.from({ length: 5 }).map((_, i) => (
            <Box key={i} display="flex" alignItems="center" gap={1}>
              <Skeleton variant="circular" width={12} height={12} />
              <Skeleton variant="text" width={80} height={16} />
            </Box>
          ))}
        </Box>
      </Paper>
    </Box>
  );
}
