"use client";

import { useState, useMemo } from "react";
import { useList } from "@refinedev/core";
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
} from "@mui/material";
import RiskBadge from "@/components/RiskBadge";

interface HealthAlert {
  id: string;
  date: string;
  farmer: string;
  animal: string;
  symptoms: string;
  risk_level: string;
  recommended_action: string;
}

const mockAlerts: HealthAlert[] = [
  { id: "H001", date: "2026-04-08", farmer: "Parvathi Amma", animal: "Sheru (Goat)", symptoms: "Fever, mouth sores, salivation", risk_level: "critical", recommended_action: "Isolate immediately, contact vet for FMD testing" },
  { id: "H002", date: "2026-04-08", farmer: "Shivamma R", animal: "Kamala (Buffalo)", symptoms: "Swollen udder, reduced milk yield", risk_level: "high", recommended_action: "Mastitis treatment, antibiotic course" },
  { id: "H003", date: "2026-04-07", farmer: "Krishna Murthy", animal: "Raja (Cattle)", symptoms: "High fever, tick infestation", risk_level: "high", recommended_action: "Anti-parasitic treatment, dipping" },
  { id: "H004", date: "2026-04-07", farmer: "Meenakshi H", animal: "Chinna (Sheep)", symptoms: "Diarrhea, loss of appetite", risk_level: "medium", recommended_action: "Deworming, monitor for 48 hours" },
  { id: "H005", date: "2026-04-06", farmer: "Lakshmi Devi", animal: "Gauri (Buffalo)", symptoms: "Slight lameness, hoof cracks", risk_level: "medium", recommended_action: "Hoof trimming, zinc supplement" },
  { id: "H006", date: "2026-04-06", farmer: "Manjunath K", animal: "Meenu (Goat)", symptoms: "Nasal discharge, coughing", risk_level: "critical", recommended_action: "PPR suspected, isolate and vaccinate herd" },
  { id: "H007", date: "2026-04-05", farmer: "Ramesh Gowda", animal: "Lakshmi (Cattle)", symptoms: "Skin nodules on neck, chest", risk_level: "high", recommended_action: "Lumpy Skin Disease protocol, report to AHD" },
  { id: "H008", date: "2026-04-05", farmer: "Nagaraj P", animal: "Bhadra (Cattle)", symptoms: "Mild bloating after feeding", risk_level: "low", recommended_action: "Adjust feed, add probiotics" },
  { id: "H009", date: "2026-04-04", farmer: "Suresh Babu", animal: "Sundari (Cattle)", symptoms: "Weight loss, rough coat", risk_level: "medium", recommended_action: "Blood test for brucellosis" },
  { id: "H010", date: "2026-04-03", farmer: "Basavaraju N", animal: "Kokila (Poultry)", symptoms: "Reduced egg production, lethargy", risk_level: "low", recommended_action: "Vitamin supplement, check ventilation" },
];

export default function HealthPage() {
  const [riskFilter, setRiskFilter] = useState("All");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const { data } = useList<HealthAlert>({ resource: "health" });
  const alerts = data?.data ?? mockAlerts;

  const filtered = useMemo(() => {
    const result = alerts.filter(
      (a) => riskFilter === "All" || a.risk_level === riskFilter.toLowerCase()
    );
    return result.sort((a, b) => b.date.localeCompare(a.date));
  }, [alerts, riskFilter]);

  return (
    <Box p={3}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Health Alerts
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        {filtered.length} active alerts,{" "}
        {alerts.filter((a) => a.risk_level === "critical").length} critical
      </Typography>

      <Paper sx={{ borderRadius: 2 }}>
        <Box p={2}>
          <Stack direction="row" spacing={2}>
            <FormControl size="small" sx={{ minWidth: 160 }}>
              <InputLabel>Risk Level</InputLabel>
              <Select
                value={riskFilter}
                label="Risk Level"
                onChange={(e) => {
                  setRiskFilter(e.target.value);
                  setPage(0);
                }}
              >
                <MenuItem value="All">All</MenuItem>
                <MenuItem value="Critical">Critical</MenuItem>
                <MenuItem value="High">High</MenuItem>
                <MenuItem value="Medium">Medium</MenuItem>
                <MenuItem value="Low">Low</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </Box>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 700 }}>Date</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Farmer</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Animal</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Symptoms</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Risk Level</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Recommended Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filtered
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((alert) => (
                  <TableRow key={alert.id} hover>
                    <TableCell sx={{ whiteSpace: "nowrap" }}>
                      {new Date(alert.date).toLocaleDateString("en-IN")}
                    </TableCell>
                    <TableCell>{alert.farmer}</TableCell>
                    <TableCell>{alert.animal}</TableCell>
                    <TableCell sx={{ maxWidth: 220 }}>{alert.symptoms}</TableCell>
                    <TableCell>
                      <RiskBadge level={alert.risk_level} />
                    </TableCell>
                    <TableCell sx={{ maxWidth: 280, fontSize: 13 }}>
                      {alert.recommended_action}
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={filtered.length}
          page={page}
          onPageChange={(_, p) => setPage(p)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </Paper>
    </Box>
  );
}
