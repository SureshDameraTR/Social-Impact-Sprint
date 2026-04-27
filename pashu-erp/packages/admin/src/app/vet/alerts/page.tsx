"use client";

import { useState, useMemo, useEffect, useCallback } from "react";
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
  Button,
  Chip,
} from "@mui/material";
import Link from "next/link";
import GISMap, { MapPoint } from "@/components/GISMap";
import RiskBadge from "@/components/RiskBadge";
import EmptyState from "@/components/EmptyState";
import { getCsrfToken } from "@/providers/auth-provider";
import { colors, sxCodeCell } from "@/theme/theme";
import { fmtDate } from "@/utils/format";

/* ---------- Types ---------- */

interface CommunityAlert {
  id: string;
  disease_name: string;
  severity: "critical" | "high" | "medium" | "low";
  location: string;
  lat?: number;
  lng?: number;
  lon?: number;
  reported_at: string;
  status: string;
  verified: boolean;
  consultation_id?: string;
}

interface HealthEvent {
  id: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low";
  location: string;
  lat?: number;
  lng?: number;
  lon?: number;
  event_date: string;
  status: string;
  consultation_id?: string;
  risk_score?: number;
}

interface AlertsResponse {
  district_name: string;
  community_alerts: CommunityAlert[];
  health_events: HealthEvent[];
}

type UnifiedRow = {
  id: string;
  rowType: "community_alert" | "health_event";
  label: string;
  severity: "critical" | "high" | "medium" | "low";
  location: string;
  date: string;
  status: string;
  verified?: boolean;
  consultationId?: string;
};

type SortKey = "severity" | "date";

const severityOrder: Record<string, number> = {
  critical: 4,
  high: 3,
  medium: 2,
  low: 1,
};

const API_URL = process.env.NEXT_PUBLIC_API_URL;

/* ---------- Component ---------- */

export default function DistrictAlertsPage() {
  const [severityFilter, setSeverityFilter] = useState("All");
  const [typeFilter, setTypeFilter] = useState("All");
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [sortBy, setSortBy] = useState<SortKey>("date");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [verifyingId, setVerifyingId] = useState<string | null>(null);

  const { data, isLoading, isError, refetch } = useList<AlertsResponse>({
    resource: "vet/dashboard/alerts",
  });

  const raw = data?.data?.[0];
  const districtName = raw?.district_name ?? "Your District";
  const communityAlerts: CommunityAlert[] = raw?.community_alerts ?? [];
  const healthEvents: HealthEvent[] = raw?.health_events ?? [];

  /* ---- Map points ---- */
  const mapPoints: MapPoint[] = useMemo(() => {
    const pts: MapPoint[] = [];

    communityAlerts.forEach((a) => {
      const lat = a.lat;
      const lng = a.lng ?? a.lon;
      if (lat == null || lng == null) return;
      pts.push({
        id: `ca-${a.id}`,
        lat: Number(lat),
        lng: Number(lng),
        label: a.disease_name,
        details: `${a.location} - ${a.status}`,
        severity: a.severity,
        type: "alert",
      });
    });

    healthEvents.forEach((e) => {
      const lat = e.lat;
      const lng = e.lng ?? e.lon;
      if (lat == null || lng == null) return;
      pts.push({
        id: `he-${e.id}`,
        lat: Number(lat),
        lng: Number(lng),
        label: e.description,
        details: `${e.location} - ${e.status}`,
        severity: e.severity ?? (e.risk_score != null
          ? (e.risk_score >= 0.8 ? "critical" : e.risk_score >= 0.6 ? "high" : e.risk_score >= 0.3 ? "medium" : "low")
          : "medium"),
        type: "alert",
      });
    });

    return pts;
  }, [communityAlerts, healthEvents]);

  /* ---- Unified table rows ---- */
  const allRows: UnifiedRow[] = useMemo(() => {
    const rows: UnifiedRow[] = [];

    communityAlerts.forEach((a) => {
      rows.push({
        id: a.id,
        rowType: "community_alert",
        label: a.disease_name,
        severity: a.severity,
        location: a.location,
        date: a.reported_at,
        status: a.status,
        verified: a.verified,
        consultationId: a.consultation_id,
      });
    });

    healthEvents.forEach((e) => {
      rows.push({
        id: e.id,
        rowType: "health_event",
        label: e.description,
        severity: e.severity ?? (e.risk_score != null
          ? (e.risk_score >= 0.8 ? "critical" : e.risk_score >= 0.6 ? "high" : e.risk_score >= 0.3 ? "medium" : "low")
          : "medium"),
        location: e.location,
        date: e.event_date,
        status: e.status,
        consultationId: e.consultation_id,
      });
    });

    return rows;
  }, [communityAlerts, healthEvents]);

  /* ---- Filter + sort ---- */
  const handleSort = (key: SortKey) => {
    if (sortBy === key) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortBy(key);
      setSortDir("asc");
    }
  };

  const filtered = useMemo(() => {
    return allRows.filter((r) => {
      if (severityFilter !== "All" && r.severity !== severityFilter.toLowerCase()) return false;
      if (typeFilter === "Community Alerts" && r.rowType !== "community_alert") return false;
      if (typeFilter === "Health Events" && r.rowType !== "health_event") return false;
      return true;
    });
  }, [allRows, severityFilter, typeFilter]);

  const sortedRows = useMemo(() => {
    const sorted = [...filtered];
    sorted.sort((a, b) => {
      if (sortBy === "severity") {
        const cmp = (severityOrder[a.severity] ?? 0) - (severityOrder[b.severity] ?? 0);
        return sortDir === "asc" ? cmp : -cmp;
      }
      const cmp = (a.date || "").localeCompare(b.date || "");
      return sortDir === "asc" ? cmp : -cmp;
    });
    return sorted;
  }, [filtered, sortBy, sortDir]);

  /* ---- Verify action ---- */
  const handleVerify = useCallback(async (alertId: string) => {
    if (!API_URL) return;
    setVerifyingId(alertId);
    try {
      const res = await fetch(`${API_URL}/alerts/${alertId}/verify`, {
        method: "PATCH",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": getCsrfToken(),
        },
      });
      if (!res.ok) throw new Error(`Verify failed: ${res.status}`);
      refetch();
    } catch {
      // Silently fail; the row stays unverified and the user can retry
    } finally {
      setVerifyingId(null);
    }
  }, [refetch]);

  /* ---- Counts ---- */
  const criticalCount = allRows.filter((r) => r.severity === "critical").length;

  /* ---- Loading / error states ---- */
  if (isLoading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 8 }} role="status" aria-label="Loading district alerts">
        <CircularProgress />
      </Box>
    );
  }

  if (isError) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error">Failed to load district alerts from server.</Alert>
      </Box>
    );
  }

  /* ---- Render ---- */
  return (
    <Box p={3}>
      {/* Header */}
      <Typography variant="h4" gutterBottom sx={{ color: colors.text }}>
        District Alerts
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={2}>
        {districtName} &mdash; {allRows.length} alerts, {criticalCount} critical
      </Typography>

      {/* Map section */}
      <Paper sx={{ overflow: "hidden", mb: 3 }}>
        {mapPoints.length === 0 ? (
          <Typography color="text.secondary" sx={{ p: 4, textAlign: "center" }}>
            No geo-located alerts in this district.
          </Typography>
        ) : (
          <GISMap
            center={[13.0, 76.5]}
            zoom={9}
            points={mapPoints}
            height="calc(60vh - 80px)"
            showLayers
          />
        )}
      </Paper>

      {/* Legend */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography
          sx={{
            fontSize: "12px",
            fontWeight: 600,
            color: colors.text,
            mb: 1,
            textTransform: "uppercase",
            letterSpacing: "0.05em",
          }}
        >
          Legend
        </Typography>
        <Box display="flex" gap={3} flexWrap="wrap">
          {[
            { color: colors.accentRed, label: "Critical" },
            { color: colors.accentAmber, label: "High" },
            { color: colors.accentAmber, label: "Medium" },
            { color: colors.accentGreen, label: "Low" },
          ].map((item) => (
            <Box key={item.label} display="flex" alignItems="center" gap={1}>
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: "50%",
                  backgroundColor: item.color,
                }}
              />
              <Typography sx={{ fontSize: "12px", color: colors.textDim }}>
                {item.label}
              </Typography>
            </Box>
          ))}
        </Box>
      </Paper>

      {/* Alerts table */}
      <Paper>
        <Box p={2}>
          <Stack direction="row" spacing={2}>
            <FormControl size="small" sx={{ minWidth: 160 }}>
              <InputLabel>Severity</InputLabel>
              <Select
                value={severityFilter}
                label="Severity"
                onChange={(e) => {
                  setSeverityFilter(e.target.value);
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
            <FormControl size="small" sx={{ minWidth: 180 }}>
              <InputLabel>Type</InputLabel>
              <Select
                value={typeFilter}
                label="Type"
                onChange={(e) => {
                  setTypeFilter(e.target.value);
                  setPage(0);
                }}
              >
                <MenuItem value="All">All</MenuItem>
                <MenuItem value="Community Alerts">Community Alerts</MenuItem>
                <MenuItem value="Health Events">Health Events</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </Box>

        <TableContainer>
          <Table aria-label="District alerts">
            <TableHead>
              <TableRow>
                <TableCell>Type</TableCell>
                <TableCell>Disease / Description</TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortBy === "severity"}
                    direction={sortBy === "severity" ? sortDir : "asc"}
                    onClick={() => handleSort("severity")}
                  >
                    Severity
                  </TableSortLabel>
                </TableCell>
                <TableCell>Location</TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortBy === "date"}
                    direction={sortBy === "date" ? sortDir : "asc"}
                    onClick={() => handleSort("date")}
                  >
                    Date
                  </TableSortLabel>
                </TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedRows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} sx={{ border: 0 }}>
                    <EmptyState />
                  </TableCell>
                </TableRow>
              ) : (
                sortedRows
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((row) => (
                    <TableRow key={`${row.rowType}-${row.id}`}>
                      <TableCell>
                        <Chip
                          label={row.rowType === "community_alert" ? "Community" : "Health"}
                          size="small"
                          sx={{
                            bgcolor:
                              row.rowType === "community_alert"
                                ? colors.warningLight
                                : colors.infoLight,
                            color:
                              row.rowType === "community_alert"
                                ? colors.accentAmber
                                : colors.accentBlue,
                            fontWeight: 600,
                            fontSize: "11px",
                          }}
                        />
                      </TableCell>
                      <TableCell sx={{ fontWeight: 500, color: colors.text, maxWidth: 240 }}>
                        {row.label}
                      </TableCell>
                      <TableCell>
                        <RiskBadge level={row.severity} />
                      </TableCell>
                      <TableCell sx={{ fontSize: "12.5px", color: colors.textDim }}>
                        {row.location}
                      </TableCell>
                      <TableCell sx={{ ...sxCodeCell, whiteSpace: "nowrap" }}>
                        {fmtDate(row.date)}
                      </TableCell>
                      <TableCell sx={{ fontSize: "12.5px", color: colors.textDim, textTransform: "capitalize" }}>
                        {row.status}
                      </TableCell>
                      <TableCell align="right">
                        {row.rowType === "community_alert" && !row.verified ? (
                          <Button
                            size="small"
                            variant="outlined"
                            disabled={verifyingId === row.id}
                            onClick={() => handleVerify(row.id)}
                            sx={{
                              fontSize: "11px",
                              fontWeight: 600,
                              borderColor: colors.primary,
                              color: colors.primary,
                              "&:hover": {
                                bgcolor: colors.primaryLight,
                                borderColor: colors.primary,
                              },
                            }}
                          >
                            {verifyingId === row.id ? "Verifying..." : "Verify"}
                          </Button>
                        ) : row.rowType === "community_alert" && row.verified ? (
                          <Chip
                            label="Verified"
                            size="small"
                            sx={{
                              bgcolor: colors.successLight,
                              color: colors.accentGreen,
                              fontWeight: 600,
                              fontSize: "11px",
                            }}
                          />
                        ) : row.consultationId ? (
                          <Button
                            component={Link}
                            href={`/vet/cases/${row.consultationId}`}
                            size="small"
                            variant="outlined"
                            sx={{
                              fontSize: "11px",
                              fontWeight: 600,
                              borderColor: colors.accentBlue,
                              color: colors.accentBlue,
                              "&:hover": {
                                bgcolor: colors.infoLight,
                                borderColor: colors.accentBlue,
                              },
                            }}
                          >
                            View Case
                          </Button>
                        ) : (
                          <Typography sx={{ fontSize: "11px", color: colors.textLight }}>
                            &mdash;
                          </Typography>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <TablePagination
          component="div"
          count={sortedRows.length}
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
