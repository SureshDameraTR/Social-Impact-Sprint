import { Box, Grid, Paper, Skeleton } from "@mui/material";

/** Loading skeleton for the Vet Dashboard page. */
export default function VetLoading() {
  return (
    <Box p={3}>
      <Skeleton variant="text" width={200} height={40} sx={{ mb: 0.5 }} />
      <Skeleton variant="text" width={320} height={24} sx={{ mb: 3 }} />

      {/* Stat cards */}
      <Grid container spacing={2.5} mb={4}>
        {Array.from({ length: 4 }).map((_, i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
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

      {/* Cases table and map */}
      <Grid container spacing={2.5}>
        <Grid item xs={12} lg={7}>
          <Paper sx={{ p: 3 }}>
            <Skeleton variant="text" width={180} height={24} sx={{ mb: 2 }} />
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} height={48} sx={{ mb: 0.5 }} />
            ))}
          </Paper>
        </Grid>
        <Grid item xs={12} lg={5}>
          <Paper sx={{ p: 3 }}>
            <Skeleton variant="text" width={180} height={24} sx={{ mb: 2 }} />
            <Skeleton variant="rectangular" height={380} sx={{ borderRadius: 1 }} />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
