import { Box, Paper, Skeleton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";

/** Loading skeleton for the Vet Cases list page. */
export default function VetCasesLoading() {
  return (
    <Box p={3}>
      <Skeleton variant="text" width={160} height={40} sx={{ mb: 0.5 }} />
      <Skeleton variant="text" width={340} height={24} sx={{ mb: 3 }} />

      <Paper>
        {/* Tab bar */}
        <Box sx={{ borderBottom: 1, borderColor: "divider", px: 2, py: 1 }}>
          <Box display="flex" gap={3}>
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} variant="text" width={80} height={24} />
            ))}
          </Box>
        </Box>

        {/* Table */}
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                {["Farmer", "Animal", "Channel", "Priority", "Date", "Status"].map((h) => (
                  <TableCell key={h}>
                    <Skeleton variant="text" width={70} height={16} />
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {Array.from({ length: 8 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton variant="text" width={120} /></TableCell>
                  <TableCell><Skeleton variant="rectangular" width={70} height={24} sx={{ borderRadius: 2 }} /></TableCell>
                  <TableCell><Skeleton variant="rectangular" width={65} height={24} sx={{ borderRadius: 2 }} /></TableCell>
                  <TableCell><Skeleton variant="rectangular" width={65} height={24} sx={{ borderRadius: 2 }} /></TableCell>
                  <TableCell><Skeleton variant="text" width={80} /></TableCell>
                  <TableCell><Skeleton variant="rectangular" width={70} height={24} sx={{ borderRadius: 2 }} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
