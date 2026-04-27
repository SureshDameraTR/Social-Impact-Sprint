import { Box, Paper, Skeleton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";

/** Loading skeleton for the Animals list page. */
export default function AnimalsLoading() {
  return (
    <Box p={3}>
      <Skeleton variant="text" width={140} height={40} sx={{ mb: 0.5 }} />
      <Skeleton variant="text" width={280} height={24} sx={{ mb: 3 }} />

      <Paper>
        {/* Search bar area */}
        <Box p={2} display="flex" gap={2}>
          <Skeleton variant="rectangular" width={300} height={40} sx={{ borderRadius: 1 }} />
          <Skeleton variant="rectangular" width={160} height={40} sx={{ borderRadius: 1 }} />
        </Box>

        {/* Table skeleton */}
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                {["Name", "Species", "Breed", "Owner ID", "Pashu Aadhaar", "Sex"].map((h) => (
                  <TableCell key={h}>
                    <Skeleton variant="text" width={80} height={16} />
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {Array.from({ length: 8 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton variant="text" width={120} /></TableCell>
                  <TableCell><Skeleton variant="rectangular" width={70} height={24} sx={{ borderRadius: 2 }} /></TableCell>
                  <TableCell><Skeleton variant="text" width={100} /></TableCell>
                  <TableCell><Skeleton variant="text" width={60} /></TableCell>
                  <TableCell><Skeleton variant="text" width={110} /></TableCell>
                  <TableCell><Skeleton variant="rectangular" width={50} height={24} sx={{ borderRadius: 2 }} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
