import { Box, Paper, Skeleton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";

/** Loading skeleton for the Health Alerts page. */
export default function HealthLoading() {
  return (
    <Box p={3}>
      <Skeleton variant="text" width={180} height={40} sx={{ mb: 0.5 }} />
      <Skeleton variant="text" width={260} height={24} sx={{ mb: 3 }} />

      <Paper>
        <Box p={2}>
          <Skeleton variant="rectangular" width={160} height={40} sx={{ borderRadius: 1 }} />
        </Box>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                {["Date", "Animal ID", "Symptoms", "Risk Level", "Probable Diseases", "Action"].map((h) => (
                  <TableCell key={h}>
                    <Skeleton variant="text" width={90} height={16} />
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {Array.from({ length: 8 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton variant="text" width={80} /></TableCell>
                  <TableCell><Skeleton variant="text" width={60} /></TableCell>
                  <TableCell><Skeleton variant="text" width={180} /></TableCell>
                  <TableCell><Skeleton variant="rectangular" width={65} height={24} sx={{ borderRadius: 2 }} /></TableCell>
                  <TableCell><Skeleton variant="text" width={140} /></TableCell>
                  <TableCell><Skeleton variant="text" width={200} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
