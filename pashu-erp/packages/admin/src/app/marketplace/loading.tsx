import { Box, Grid, Paper, Skeleton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";

/** Loading skeleton for the Marketplace page. */
export default function MarketplaceLoading() {
  return (
    <Box p={3}>
      <Skeleton variant="text" width={180} height={40} sx={{ mb: 0.5 }} />
      <Skeleton variant="text" width={340} height={24} sx={{ mb: 3 }} />

      {/* Stat cards */}
      <Grid container spacing={2.5} mb={3}>
        {Array.from({ length: 3 }).map((_, i) => (
          <Grid item xs={12} sm={4} key={i}>
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

      {/* Chart skeleton */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Skeleton variant="text" width={200} height={24} sx={{ mb: 2 }} />
        <Skeleton variant="rectangular" height={220} sx={{ borderRadius: 1 }} />
      </Paper>

      {/* Table skeleton */}
      <Paper>
        <Box p={2}>
          <Skeleton variant="rectangular" width={320} height={40} sx={{ borderRadius: 1 }} />
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                {["Date", "Farmer", "Product", "Qty", "Price/Unit", "Total", "Buyer"].map((h) => (
                  <TableCell key={h}>
                    <Skeleton variant="text" width={70} height={16} />
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {Array.from({ length: 6 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton variant="text" width={80} /></TableCell>
                  <TableCell><Skeleton variant="text" width={60} /></TableCell>
                  <TableCell><Skeleton variant="rectangular" width={70} height={24} sx={{ borderRadius: 2 }} /></TableCell>
                  <TableCell><Skeleton variant="text" width={50} /></TableCell>
                  <TableCell><Skeleton variant="text" width={60} /></TableCell>
                  <TableCell><Skeleton variant="text" width={70} /></TableCell>
                  <TableCell><Skeleton variant="text" width={90} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
