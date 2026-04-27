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
  TableSortLabel,
  CircularProgress,
  Alert,
} from "@mui/material";
import RiskBadge from "@/components/RiskBadge";
import { colors, sxCodeCell, sxNameCell } from "@/theme/theme";
import { fmtDate } from "@/utils/format";
import EmptyState from "@/components/EmptyState";

interface HealthAlert {
  id: string;
  event_date: string;
  recorded_by: string;
  animal_id: string;
  symptoms: string[];
  ai_risk_score: number;
  recommended_action: string;
  event_type: string;
  probable_diseases: string[];
}

type SortKey = "event_date" | "ai_risk_score";

function riskLabel(score: number): string {
  if (score >= 0.8) return "critical";
  if (score >= 0.6) return "high";
  if (score >= 0.3) return "medium";
  return "low";
}

export default function HealthPage() {
  const [riskFilter, setRiskFilter] = useState("All");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [sortBy, setSortBy] = useState<SortKey>("event_date");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const { data, isLoading, isError } = useList<HealthAlert>({
    resource: "health",
    pagination: { current: page + 1, pageSize: rowsPerPage },
    sorters: [{ field: sortBy, order: sortDir }],
  });

  const alerts = data?.data ?? [];
  const serverTotal = data?.total ?? 0;

  const handleSort = (key: SortKey) => {
    if (sortBy === key) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortBy(key);
      setSortDir("asc");
    }
    setPage(0);
  };

  const filtered = useMemo(() => {
    return alerts.filter(
      (a) => riskFilter === "All" || riskLabel(a.ai_risk_score) === riskFilter.toLowerCase()
    );
  }, [alerts, riskFilter]);

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 8 }} role="status" aria-label="Loading health alerts"><CircularProgress /></Box>;
  if (isError) return <Box sx={{ p: 4 }}><Alert severity="error">Failed to load data from server.</Alert></Box>;

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ color: colors.text }}>
        Health Alerts
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        {filtered.length} active alerts,{" "}
        {alerts.filter((a) => a.ai_risk_score >= 0.8).length} critical
      </Typography>

      <Paper>
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
          <Table aria-label="Health alerts table">
            <TableHead>
              <TableRow>
                <TableCell>
                  <TableSortLabel active={sortBy === "event_date"} direction={sortBy === "event_date" ? sortDir : "asc"} onClick={() => handleSort("event_date")}>
                    Date
                  </TableSortLabel>
                </TableCell>
                <TableCell>Animal ID</TableCell>
                <TableCell>Symptoms</TableCell>
                <TableCell>
                  <TableSortLabel active={sortBy === "ai_risk_score"} direction={sortBy === "ai_risk_score" ? sortDir : "asc"} onClick={() => handleSort("ai_risk_score")}>
                    Risk Level
                  </TableSortLabel>
                </TableCell>
                <TableCell>Probable Diseases</TableCell>
                <TableCell>Recommended Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} sx={{ border: 0 }}>
                    <EmptyState />
                  </TableCell>
                </TableRow>
              ) : (
                filtered.map((alert) => (
                    <TableRow key={alert.id}>
                      <TableCell
                        sx={{ ...sxCodeCell, whiteSpace: "nowrap" }}
                      >
                        {fmtDate(alert.event_date)}
                      </TableCell>
                      <TableCell sx={{ fontSize: '11px', color: colors.textDim }}>{alert.animal_id?.slice(0, 8)}</TableCell>
                      <TableCell sx={{ maxWidth: 220, fontSize: '12.5px', color: colors.textDim }}>
                        {Array.isArray(alert.symptoms)
                          ? alert.symptoms.join(", ")
                          : typeof alert.symptoms === "object" && alert.symptoms
                            ? Object.keys(alert.symptoms).join(", ")
                            : String(alert.symptoms ?? "\u2014")}
                      </TableCell>
                      <TableCell>
                        <RiskBadge level={riskLabel(alert.ai_risk_score)} />
                      </TableCell>
                      <TableCell sx={{ maxWidth: 180, fontSize: '12.5px', color: colors.textDim }}>
                        {Array.isArray(alert.probable_diseases)
                          ? alert.probable_diseases
                              .map((d) => (typeof d === "object" && d !== null ? (d as Record<string, unknown>).name ?? (d as Record<string, unknown>).disease ?? JSON.stringify(d) : String(d)))
                              .join(", ")
                          : typeof alert.probable_diseases === "object" && alert.probable_diseases
                            ? Object.keys(alert.probable_diseases).join(", ")
                            : String(alert.probable_diseases ?? "\u2014")}
                      </TableCell>
                      <TableCell sx={{ maxWidth: 280, fontSize: '12.5px', color: colors.textDim }}>
                        {alert.recommended_action}
                      </TableCell>
                    </TableRow>
                  ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={riskFilter !== "All" ? filtered.length : serverTotal}
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
