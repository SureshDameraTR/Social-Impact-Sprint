import { Box, Paper, Skeleton, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";

/** Loading skeleton for the Farmers list page. */
export default function FarmersLoading() {
  return (
    <Box p={3}>
      <Skeleton variant="text" width={140} height={40} sx={{ mb: 0.5 }} />
      <Skeleton variant="text" width={300} height={24} sx={{ mb: 3 }} />

      <Paper>
        <Box p={2}>
          <Skeleton variant="rectangular" width={320} height={40} sx={{ borderRadius: 1 }} />
        </Box>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                {["Name", "Phone", "District", "Village", "Animals", "Registered"].map((h) => (
                  <TableCell key={h}>
                    <Skeleton variant="text" width={80} height={16} />
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {Array.from({ length: 8 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1.5}>
                      <Skeleton variant="circular" width={30} height={30} />
                      <Skeleton variant="text" width={120} />
                    </Box>
                  </TableCell>
                  <TableCell><Skeleton variant="text" width={100} /></TableCell>
                  <TableCell><Skeleton variant="rectangular" width={70} height={24} sx={{ borderRadius: 2 }} /></TableCell>
                  <TableCell><Skeleton variant="text" width={80} /></TableCell>
                  <TableCell align="center"><Skeleton variant="rectangular" width={30} height={24} sx={{ borderRadius: 2, mx: "auto" }} /></TableCell>
                  <TableCell><Skeleton variant="text" width={80} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
