import { Box, Paper, Skeleton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";

/** Loading skeleton for the Government Schemes page. */
export default function SchemesLoading() {
  return (
    <Box p={3}>
      <Skeleton variant="text" width={220} height={40} sx={{ mb: 0.5 }} />
      <Skeleton variant="text" width={300} height={24} sx={{ mb: 3 }} />

      <Paper>
        <Box p={2}>
          <Skeleton variant="rectangular" width={320} height={40} sx={{ borderRadius: 1 }} />
        </Box>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                {["Code", "Name", "Ministry", "Max Subsidy", "Subsidy %", "Active", "Valid Period"].map((h) => (
                  <TableCell key={h}>
                    <Skeleton variant="text" width={80} height={16} />
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {Array.from({ length: 8 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton variant="text" width={70} /></TableCell>
                  <TableCell><Skeleton variant="text" width={200} /></TableCell>
                  <TableCell><Skeleton variant="rectangular" width={100} height={24} sx={{ borderRadius: 2 }} /></TableCell>
                  <TableCell><Skeleton variant="text" width={80} /></TableCell>
                  <TableCell><Skeleton variant="text" width={40} /></TableCell>
                  <TableCell><Skeleton variant="rectangular" width={60} height={24} sx={{ borderRadius: 2 }} /></TableCell>
                  <TableCell><Skeleton variant="text" width={140} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
