import { Box, Paper, Skeleton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";

/** Loading skeleton for the District Alerts page. */
export default function DistrictAlertsLoading() {
  return (
    <Box p={3}>
      <Skeleton variant="text" width={200} height={40} sx={{ mb: 0.5 }} />
      <Skeleton variant="text" width={280} height={24} sx={{ mb: 2 }} />

      {/* Map skeleton */}
      <Paper sx={{ overflow: "hidden", mb: 3 }}>
        <Skeleton variant="rectangular" height="calc(60vh - 80px)" sx={{ borderRadius: 0, minHeight: 300 }} />
      </Paper>

      {/* Legend */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Skeleton variant="text" width={60} height={16} sx={{ mb: 1 }} />
        <Box display="flex" gap={3}>
          {Array.from({ length: 4 }).map((_, i) => (
            <Box key={i} display="flex" alignItems="center" gap={1}>
              <Skeleton variant="circular" width={12} height={12} />
              <Skeleton variant="text" width={60} height={16} />
            </Box>
          ))}
        </Box>
      </Paper>

      {/* Table skeleton */}
      <Paper>
        <Box p={2} display="flex" gap={2}>
          <Skeleton variant="rectangular" width={160} height={40} sx={{ borderRadius: 1 }} />
          <Skeleton variant="rectangular" width={180} height={40} sx={{ borderRadius: 1 }} />
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                {["Type", "Disease", "Severity", "Location", "Date", "Status", "Action"].map((h) => (
                  <TableCell key={h}>
                    <Skeleton variant="text" width={70} height={16} />
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {Array.from({ length: 6 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton variant="rectangular" width={70} height={24} sx={{ borderRadius: 2 }} /></TableCell>
                  <TableCell><Skeleton variant="text" width={160} /></TableCell>
                  <TableCell><Skeleton variant="rectangular" width={65} height={24} sx={{ borderRadius: 2 }} /></TableCell>
                  <TableCell><Skeleton variant="text" width={100} /></TableCell>
                  <TableCell><Skeleton variant="text" width={80} /></TableCell>
                  <TableCell><Skeleton variant="text" width={70} /></TableCell>
                  <TableCell><Skeleton variant="rectangular" width={60} height={30} sx={{ borderRadius: 1 }} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
