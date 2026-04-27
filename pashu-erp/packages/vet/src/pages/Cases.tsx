import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Skeleton,
  Alert,
  IconButton,
  Tooltip,
} from "@mui/material";
import RefreshIcon from "@mui/icons-material/Refresh";
import SpeciesChip from "../components/SpeciesChip";
import EmptyState from "../components/EmptyState";
import { colors } from "../theme";
import { fmtDateTime } from "../utils/format";
import { getCases, type VetCase } from "../api/vet";

const STATUS_TABS = [
  { label: "All", value: "" },
  { label: "Pending", value: "pending" },
  { label: "In Review", value: "in_review" },
  { label: "Diagnosed", value: "diagnosed" },
  { label: "Closed", value: "closed" },
];

export default function Cases() {
  const navigate = useNavigate();
  const [tab, setTab] = useState(0);
  const [cases, setCases] = useState<VetCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const statusFilter = STATUS_TABS[tab].value;

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await getCases(statusFilter || undefined);
      setCases(res.data.data);
    } catch {
      setError("Failed to load cases");
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => { load(); }, [load]);

  const statusChip = (status: string) => {
    const key = status as keyof typeof colors;
    const c = colors[key] || colors.routine;
    return <Chip label={status.replace("_", " ")} size="small" sx={{ bgcolor: c.bg, color: c.text, fontWeight: 600, fontSize: "11px", textTransform: "capitalize" }} />;
  };

  const priorityChip = (priority: string) => {
    const key = priority as keyof typeof colors;
    const c = colors[key] || colors.routine;
    return <Chip label={priority} size="small" sx={{ bgcolor: c.bg, color: c.text, fontWeight: 600, fontSize: "11px", textTransform: "capitalize" }} />;
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: "auto" }}>
      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h5" fontWeight={700}>
          Cases
        </Typography>
        <Tooltip title="Refresh">
          <span>
            <IconButton onClick={load} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </span>
        </Tooltip>
      </Box>

      <Tabs
        value={tab}
        onChange={(_, v) => setTab(v)}
        sx={{ mb: 2, borderBottom: 1, borderColor: "divider" }}
      >
        {STATUS_TABS.map((t) => (
          <Tab key={t.value} label={t.label} sx={{ textTransform: "none", fontWeight: 600 }} />
        ))}
      </Tabs>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {loading ? (
        <Skeleton variant="rounded" height={400} />
      ) : cases.length === 0 ? (
        <EmptyState title="No cases found" subtitle={statusFilter ? `No ${statusFilter.replace("_", " ")} cases` : "No cases yet"} />
      ) : (
        <TableContainer component={Paper} variant="outlined">
          <Table aria-label="Veterinary cases">
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 700 }}>Animal</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Farmer</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Priority</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Channel</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Created</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {cases.map((c) => (
                <TableRow
                  key={c.id}
                  hover
                  sx={{ cursor: "pointer" }}
                  onClick={() => navigate(`/cases/${c.id}`)}
                >
                  <TableCell>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <Typography variant="body2" fontWeight={600}>
                        {c.animal?.name || c.animal_id.slice(0, 8)}
                      </Typography>
                      {c.animal && <SpeciesChip species={c.animal.species} />}
                    </Box>
                  </TableCell>
                  <TableCell>{c.farmer?.name || "—"}</TableCell>
                  <TableCell>{statusChip(c.status)}</TableCell>
                  <TableCell>{priorityChip(c.priority)}</TableCell>
                  <TableCell>
                    <Chip
                      label={c.channel.replace("_", " ")}
                      size="small"
                      sx={{
                        bgcolor: (colors[c.channel as keyof typeof colors] || colors.routine).bg,
                        color: (colors[c.channel as keyof typeof colors] || colors.routine).text,
                        fontWeight: 600,
                        fontSize: "11px",
                        textTransform: "capitalize",
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {fmtDateTime(c.created_at)}
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
