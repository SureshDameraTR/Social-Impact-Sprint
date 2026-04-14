import { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Skeleton,
  Alert,
  Tabs,
  Tab,
} from "@mui/material";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import VerifiedIcon from "@mui/icons-material/Verified";
import EmptyState from "../components/EmptyState";
import { fmtDateTime } from "../utils/format";
import { getDashboardAlerts, verifyAlert, type AlertItem, type HealthEvent } from "../api/vet";

const SEVERITY_COLORS: Record<string, { bg: string; text: string }> = {
  critical: { bg: "#ffebee", text: "#c62828" },
  high: { bg: "#fff3e0", text: "#e65100" },
  medium: { bg: "#fff8e1", text: "#f57f17" },
  low: { bg: "#e8f5e9", text: "#2e7d32" },
};

export default function Alerts() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [events, setEvents] = useState<HealthEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [tab, setTab] = useState(0);
  const [verifying, setVerifying] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const res = await getDashboardAlerts();
        if (cancelled) return;
        setAlerts(res.data.community_alerts);
        setEvents(res.data.health_events);
      } catch {
        if (!cancelled) setError("Failed to load alerts");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  const handleVerify = async (alertId: string) => {
    setVerifying(alertId);
    try {
      await verifyAlert(alertId);
      setAlerts((prev) =>
        prev.map((a) => (a.id === alertId ? { ...a, status: "verified" } : a))
      );
    } catch {
      setError("Failed to verify alert");
    } finally {
      setVerifying(null);
    }
  };

  const severityChip = (severity: string) => {
    const c = SEVERITY_COLORS[severity] || SEVERITY_COLORS.medium;
    return (
      <Chip
        label={severity}
        size="small"
        sx={{ bgcolor: c.bg, color: c.text, fontWeight: 600, fontSize: "11px", textTransform: "capitalize" }}
      />
    );
  };

  const riskBadge = (score: number | null) => {
    if (score === null) return "—";
    const color = score >= 0.7 ? "#c62828" : score >= 0.4 ? "#e65100" : "#2e7d32";
    return (
      <Chip
        label={`${(score * 100).toFixed(0)}%`}
        size="small"
        sx={{ bgcolor: `${color}15`, color, fontWeight: 700, fontSize: "11px" }}
      />
    );
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: "auto" }}>
      <Typography variant="h5" fontWeight={700} sx={{ mb: 3 }}>
        District Alerts
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError("")}>{error}</Alert>}

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3, borderBottom: 1, borderColor: "divider" }}>
        <Tab
          label={`Disease Alerts (${alerts.length})`}
          sx={{ textTransform: "none", fontWeight: 600 }}
        />
        <Tab
          label={`Health Events (${events.length})`}
          sx={{ textTransform: "none", fontWeight: 600 }}
        />
      </Tabs>

      {loading ? (
        <Skeleton variant="rounded" height={400} />
      ) : tab === 0 ? (
        alerts.length === 0 ? (
          <EmptyState
            icon={<WarningAmberIcon sx={{ fontSize: 48 }} />}
            title="No active disease alerts"
            subtitle="Your district is clear"
          />
        ) : (
          <Grid container spacing={2}>
            {alerts.map((alert) => (
              <Grid item xs={12} md={6} key={alert.id}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", mb: 1 }}>
                      <Box>
                        <Typography variant="subtitle1" fontWeight={700}>
                          {alert.disease_name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {alert.alert_type} &middot; {alert.location_name || "Unknown location"}
                        </Typography>
                      </Box>
                      {severityChip(alert.severity)}
                    </Box>

                    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mt: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        {fmtDateTime(alert.created_at)}
                      </Typography>

                      {alert.status === "verified" ? (
                        <Chip
                          icon={<VerifiedIcon />}
                          label="Verified"
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                      ) : (
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<VerifiedIcon />}
                          onClick={() => handleVerify(alert.id)}
                          disabled={verifying === alert.id}
                        >
                          Verify
                        </Button>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )
      ) : events.length === 0 ? (
        <EmptyState title="No health events" subtitle="No recent health events in your district" />
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 700 }}>Animal ID</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Event Type</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Symptoms</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>AI Risk</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Date</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {events.map((ev) => (
                <TableRow key={ev.id}>
                  <TableCell>
                    <Typography variant="body2" fontWeight={600}>
                      {ev.animal_id.slice(0, 8)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip label={ev.event_type} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ maxWidth: 250, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {ev.symptoms || "—"}
                    </Typography>
                  </TableCell>
                  <TableCell>{riskBadge(ev.ai_risk_score)}</TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {fmtDateTime(ev.created_at)}
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
