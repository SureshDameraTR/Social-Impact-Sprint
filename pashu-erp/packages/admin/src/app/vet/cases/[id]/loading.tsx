import { Box, Grid, Card, CardContent, Paper, Skeleton, Stack } from "@mui/material";

/** Loading skeleton for the Vet Case Detail page. */
export default function VetCaseDetailLoading() {
  return (
    <Box p={3}>
      {/* Header */}
      <Stack direction="row" alignItems="center" spacing={1.5} mb={1}>
        <Skeleton variant="circular" width={32} height={32} />
        <Skeleton variant="text" width={160} height={40} />
        <Skeleton variant="rectangular" width={70} height={24} sx={{ borderRadius: 2 }} />
        <Skeleton variant="rectangular" width={65} height={24} sx={{ borderRadius: 2 }} />
        <Skeleton variant="rectangular" width={55} height={24} sx={{ borderRadius: 2 }} />
      </Stack>
      <Skeleton variant="text" width={240} height={20} sx={{ ml: 5.5, mb: 3 }} />

      <Grid container spacing={2.5}>
        {/* Left column */}
        <Grid item xs={12} md={7}>
          {/* Farmer info card */}
          <Card sx={{ mb: 2.5 }}>
            <CardContent>
              <Skeleton variant="text" width={180} height={24} sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                {Array.from({ length: 4 }).map((_, i) => (
                  <Grid item xs={6} key={i}>
                    <Skeleton variant="text" width={60} height={14} />
                    <Skeleton variant="text" width={120} height={20} sx={{ mt: 0.5 }} />
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>

          {/* Animal info card */}
          <Card sx={{ mb: 2.5 }}>
            <CardContent>
              <Skeleton variant="text" width={160} height={24} sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                {Array.from({ length: 6 }).map((_, i) => (
                  <Grid item xs={6} key={i}>
                    <Skeleton variant="text" width={60} height={14} />
                    <Skeleton variant="text" width={100} height={20} sx={{ mt: 0.5 }} />
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>

          {/* Photos card */}
          <Card sx={{ mb: 2.5 }}>
            <CardContent>
              <Skeleton variant="text" width={80} height={24} sx={{ mb: 1.5 }} />
              <Box display="grid" gridTemplateColumns="repeat(auto-fill, minmax(120px, 1fr))" gap={1.5}>
                {Array.from({ length: 3 }).map((_, i) => (
                  <Skeleton key={i} variant="rectangular" sx={{ paddingTop: "100%", borderRadius: 2 }} />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Right column */}
        <Grid item xs={12} md={5}>
          <Card sx={{ mb: 2.5 }}>
            <CardContent>
              <Skeleton variant="text" width={140} height={24} sx={{ mb: 2 }} />
              {Array.from({ length: 3 }).map((_, i) => (
                <Paper key={i} sx={{ p: 1.5, mb: 1.5 }} elevation={0}>
                  <Skeleton variant="text" width="80%" height={16} />
                  <Skeleton variant="text" width="60%" height={14} sx={{ mt: 0.5 }} />
                  <Skeleton variant="text" width="40%" height={14} sx={{ mt: 0.25 }} />
                </Paper>
              ))}
            </CardContent>
          </Card>

          <Card sx={{ mb: 2.5 }}>
            <CardContent>
              <Skeleton variant="text" width={160} height={24} sx={{ mb: 2 }} />
              {Array.from({ length: 2 }).map((_, i) => (
                <Paper key={i} sx={{ p: 1.5, mb: 1 }} elevation={0}>
                  <Skeleton variant="text" width="70%" height={16} />
                  <Skeleton variant="text" width="50%" height={14} sx={{ mt: 0.5 }} />
                </Paper>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
