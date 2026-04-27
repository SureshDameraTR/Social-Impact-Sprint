import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  List,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Chip,
  Skeleton,
  Alert,
} from "@mui/material";
import PendingActionsIcon from "@mui/icons-material/PendingActions";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import PetsIcon from "@mui/icons-material/Pets";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import ArrowForwardIosIcon from "@mui/icons-material/ArrowForwardIos";
import StatCard from "../components/StatCard";
import EmptyState from "../components/EmptyState";
import { colors } from "../theme";
import { fmtDateTime } from "../utils/format";
import { getDashboardStats, getPendingCases, type DashboardStats, type VetCase } from "../api/vet";
import { useAuth } from "../hooks/useAuth";

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [pending, setPending] = useState<VetCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [s, p] = await Promise.all([getDashboardStats(), getPendingCases(8)]);
        if (cancelled) return;
        setStats(s.data);
        setPending(p.data.data);
      } catch {
        if (!cancelled) setError("Failed to load dashboard data");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  const priorityChip = (p: string) => {
    const key = p as keyof typeof colors;
    const c = colors[key] || colors.routine;
    return <Chip label={p} size="small" sx={{ bgcolor: c.bg, color: c.text, fontWeight: 600, fontSize: "11px" }} />;
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: "auto" }}>
      <Typography variant="h5" fontWeight={700} sx={{ mb: 0.5 }}>
        Welcome, {user?.name?.startsWith("Dr.") ? user.name : `Dr. ${user?.name || "Vet"}`}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        {user?.district} District &middot; {new Date().toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long" })}
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Grid container spacing={2} sx={{ mb: 4 }}>
        {loading ? (
          [0, 1, 2, 3].map((i) => (
            <Grid item xs={6} md={3} key={i}>
              <Skeleton variant="rounded" height={100} />
            </Grid>
          ))
        ) : stats ? (
          <>
            <Grid item xs={6} md={3}>
              <StatCard label="Pending Cases" value={stats.pending_cases} icon={<PendingActionsIcon />} color={colors.urgent.text} />
            </Grid>
            <Grid item xs={6} md={3}>
              <StatCard label="Diagnosed Today" value={stats.diagnosed_today} icon={<CheckCircleIcon />} color={colors.diagnosed.text} />
            </Grid>
            <Grid item xs={6} md={3}>
              <StatCard label="District Animals" value={stats.district_animals} icon={<PetsIcon />} color={colors.in_review.text} />
            </Grid>
            <Grid item xs={6} md={3}>
              <StatCard label="Active Alerts" value={stats.active_alerts} icon={<WarningAmberIcon />} color={colors.emergency.text} />
            </Grid>
          </>
        ) : null}
      </Grid>

      <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
        Pending Cases
      </Typography>

      {loading ? (
        <Skeleton variant="rounded" height={300} />
      ) : pending.length === 0 ? (
        <EmptyState title="No pending cases" subtitle="All cases are up to date" />
      ) : (
        <Card>
          <CardContent sx={{ p: 0, "&:last-child": { pb: 0 } }}>
            <List disablePadding>
              {pending.map((c, i) => (
                <ListItemButton
                  key={c.id}
                  divider={i < pending.length - 1}
                  onClick={() => navigate(`/cases/${c.id}`)}
                  sx={{ py: 1.5 }}
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                        <Typography fontWeight={600}>
                          {c.animal?.species || "Animal"} — {c.animal?.name || c.animal_id.slice(0, 8)}
                        </Typography>
                        {priorityChip(c.priority)}
                      </Box>
                    }
                    secondary={
                      <>
                        {c.farmer?.name || "Unknown farmer"} &middot; {c.channel} &middot; {fmtDateTime(c.created_at)}
                      </>
                    }
                  />
                  <ListItemIcon sx={{ minWidth: "auto" }}>
                    <ArrowForwardIosIcon fontSize="small" color="action" />
                  </ListItemIcon>
                </ListItemButton>
              ))}
            </List>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}
