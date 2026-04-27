import { Box, Paper, Skeleton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";

/** Loading skeleton for the Milk Collection page. */
export default function MilkLoading() {
  return (
    <Box p={3}>
      <Skeleton variant="text" width={200} height={40} sx={{ mb: 0.5 }} />
      <Skeleton variant="text" width={280} height={24} sx={{ mb: 3 }} />

      {/* Chart skeleton */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Skeleton variant="text" width={220} height={24} sx={{ mb: 2 }} />
        <Skeleton variant="rectangular" height={220} sx={{ borderRadius: 1 }} />
      </Paper>

      {/* Table skeleton */}
      <Paper>
        <Box p={2} display="flex" gap={2}>
          <Skeleton variant="rectangular" width={150} height={40} sx={{ borderRadius: 1 }} />
          <Skeleton variant="rectangular" width={150} height={40} sx={{ borderRadius: 1 }} />
        </Box>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                {["Date", "Animal ID", "Quantity (L)", "Session", "Notes"].map((h) => (
                  <TableCell key={h}>
                    <Skeleton variant="text" width={80} height={16} />
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {Array.from({ length: 8 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton variant="text" width={80} /></TableCell>
                  <TableCell><Skeleton variant="text" width={60} /></TableCell>
                  <TableCell><Skeleton variant="text" width={50} /></TableCell>
                  <TableCell><Skeleton variant="rectangular" width={65} height={24} sx={{ borderRadius: 2 }} /></TableCell>
                  <TableCell><Skeleton variant="text" width={120} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
