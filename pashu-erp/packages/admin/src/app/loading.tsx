import { Box, Grid, Paper, Skeleton } from "@mui/material";

/** Root loading.tsx — shown while the dashboard page chunk downloads. */
export default function DashboardLoading() {
  return (
    <Box p={3}>
      {/* Page title */}
      <Skeleton variant="text" width={180} height={40} sx={{ mb: 0.5 }} />
      <Skeleton variant="text" width={320} height={24} sx={{ mb: 3 }} />

      {/* Stat cards row */}
      <Grid container spacing={2.5} mb={4}>
        {Array.from({ length: 6 }).map((_, i) => (
          <Grid item xs={12} sm={6} md={4} key={i}>
            <Paper sx={{ p: 2.5, display: "flex", alignItems: "center", gap: 2 }}>
              <Skeleton variant="circular" width={44} height={44} />
              <Box sx={{ flex: 1 }}>
                <Skeleton variant="text" width="60%" height={16} />
                <Skeleton variant="text" width="40%" height={28} sx={{ mt: 0.5 }} />
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* Chart and map row */}
      <Grid container spacing={2.5}>
        <Grid item xs={12} lg={7}>
          <Paper sx={{ p: 3 }}>
            <Skeleton variant="text" width={240} height={24} sx={{ mb: 2 }} />
            <Skeleton variant="rectangular" height={320} sx={{ borderRadius: 1 }} />
          </Paper>
        </Grid>
        <Grid item xs={12} lg={5}>
          <Paper sx={{ p: 3 }}>
            <Skeleton variant="text" width={180} height={24} sx={{ mb: 2 }} />
            <Skeleton variant="rectangular" height={320} sx={{ borderRadius: 1 }} />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
