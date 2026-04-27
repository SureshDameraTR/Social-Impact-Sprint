import { Box, Grid, Card, CardContent, Paper, Skeleton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";

/** Loading skeleton for the Vaccinations page. */
export default function VaccinationsLoading() {
  return (
    <Box p={3}>
      <Skeleton variant="text" width={240} height={40} sx={{ mb: 0.5 }} />
      <Skeleton variant="text" width={360} height={24} sx={{ mb: 3 }} />

      {/* Stat cards */}
      <Grid container spacing={2.5} mb={4}>
        {Array.from({ length: 3 }).map((_, i) => (
          <Grid item xs={12} sm={4} key={i}>
            <Card sx={{ borderLeft: "3px solid", borderColor: "divider" }}>
              <CardContent sx={{ textAlign: "center", py: 3 }}>
                <Skeleton variant="text" width={120} height={16} sx={{ mx: "auto", mb: 1 }} />
                <Skeleton variant="text" width={60} height={44} sx={{ mx: "auto" }} />
                <Skeleton variant="rectangular" height={8} sx={{ mt: 1.5, borderRadius: 1 }} />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Village coverage table */}
      <Skeleton variant="text" width={200} height={24} sx={{ mb: 1 }} />
      <Paper sx={{ mb: 4 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                {["Village Code", "Village Name", "Total Animals", "Vaccinated", "Coverage %", "Status"].map((h) => (
                  <TableCell key={h}>
                    <Skeleton variant="text" width={90} height={16} />
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton variant="text" width={60} /></TableCell>
                  <TableCell><Skeleton variant="text" width={100} /></TableCell>
                  <TableCell><Skeleton variant="text" width={50} /></TableCell>
                  <TableCell><Skeleton variant="text" width={50} /></TableCell>
                  <TableCell><Skeleton variant="text" width={40} /></TableCell>
                  <TableCell><Skeleton variant="rectangular" width={80} height={24} sx={{ borderRadius: 2 }} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Species breakdown */}
      <Skeleton variant="text" width={180} height={24} sx={{ mb: 1 }} />
      <Grid container spacing={2} mb={4}>
        {Array.from({ length: 4 }).map((_, i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Card>
              <CardContent>
                <Skeleton variant="text" width={100} height={20} sx={{ mb: 1.5 }} />
                <Skeleton variant="text" width="60%" height={14} sx={{ mb: 0.5 }} />
                <Skeleton variant="rectangular" height={6} sx={{ borderRadius: 1 }} />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
