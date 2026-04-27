import { Box, Grid, Card, CardContent, Paper, Skeleton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";

/** Loading skeleton for the IoT Devices page. */
export default function IotLoading() {
  return (
    <Box p={3}>
      <Skeleton variant="text" width={220} height={40} sx={{ mb: 0.5 }} />
      <Skeleton variant="text" width={300} height={24} sx={{ mb: 3 }} />

      {/* Device type cards */}
      <Grid container spacing={2.5} mb={4}>
        {Array.from({ length: 4 }).map((_, i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Card sx={{ borderLeft: "3px solid", borderColor: "divider" }}>
              <CardContent sx={{ p: 2.5 }}>
                <Skeleton variant="rectangular" width={50} height={24} sx={{ borderRadius: 2, mb: 2 }} />
                <Skeleton variant="text" width={120} height={20} />
                <Skeleton variant="text" width={80} height={16} sx={{ mb: 1 }} />
                <Box display="flex" gap={1} mb={1}>
                  <Skeleton variant="rectangular" width={80} height={24} sx={{ borderRadius: 2 }} />
                  <Skeleton variant="rectangular" width={80} height={24} sx={{ borderRadius: 2 }} />
                </Box>
                <Skeleton variant="rectangular" height={6} sx={{ borderRadius: 1, mt: 1 }} />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Telemetry table */}
      <Paper>
        <Box p={2} display="flex" justifyContent="space-between" alignItems="center">
          <Skeleton variant="text" width={200} height={20} />
          <Skeleton variant="rectangular" width={300} height={40} sx={{ borderRadius: 1 }} />
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                {["Device ID", "Animal ID", "Metrics", "Battery", "RSSI", "Timestamp"].map((h) => (
                  <TableCell key={h}>
                    <Skeleton variant="text" width={70} height={16} />
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {Array.from({ length: 6 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton variant="text" width={100} /></TableCell>
                  <TableCell><Skeleton variant="text" width={80} /></TableCell>
                  <TableCell><Skeleton variant="text" width={180} /></TableCell>
                  <TableCell align="center"><Skeleton variant="rectangular" width={45} height={24} sx={{ borderRadius: 2, mx: "auto" }} /></TableCell>
                  <TableCell><Skeleton variant="text" width={60} /></TableCell>
                  <TableCell><Skeleton variant="text" width={100} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
