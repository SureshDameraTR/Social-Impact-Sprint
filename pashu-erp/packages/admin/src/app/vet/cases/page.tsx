"use client";

import { useState, useMemo, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
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
  Tabs,
  Tab,
  Chip,
  CircularProgress,
  Alert,
} from "@mui/material";
import SpeciesChip from "@/components/SpeciesChip";
import { colors, sxCodeCell } from "@/theme/theme";
import { fmtDate } from "@/utils/format";
import EmptyState from "@/components/EmptyState";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

interface VetCaseAnimal {
  id: string;
  species: string;
  name: string | null;
  breed: string;
  owner?: {
    id: string;
    name: string;
    phone: string;
    village_code: string;
    location_district: string;
  };
}

interface VetCase {
  id: string;
  animal_id: string;
  farmer_id: string;
  vet_id: string | null;
  status: string;
  priority: string;
  channel: string;
  farmer_notes: string | null;
  photo_urls: string[] | null;
  diagnosis: string | null;
  prescription: string | null;
  follow_up_date: string | null;
  video_call_url: string | null;
  district: string;
  created_at: string;
  updated_at: string;
  animal?: VetCaseAnimal;
  farmer?: { id: string; name: string };
}

const STATUS_TABS = [
  { label: "Pending", value: "pending" },
  { label: "In Review", value: "in_review" },
  { label: "Diagnosed", value: "diagnosed" },
  { label: "Closed", value: "closed" },
] as const;

const channelConfig: Record<string, { bg: string; color: string }> = {
  photo: { bg: colors.infoLight, color: colors.accentBlue },
  walk_in: { bg: colors.successLight, color: colors.accentGreen },
  referral: { bg: colors.warningLight, color: colors.accentAmber },
};

const priorityConfig: Record<string, { bg: string; color: string }> = {
  emergency: { bg: colors.errorLight, color: colors.accentRed },
  urgent: { bg: colors.warningLight, color: colors.accentAmber },
  routine: { bg: "#f0f0f0", color: "#666" },
};

const statusConfig: Record<string, { bg: string; color: string }> = {
  pending: { bg: colors.warningLight, color: colors.accentAmber },
  in_review: { bg: colors.infoLight, color: colors.accentBlue },
  diagnosed: { bg: colors.successLight, color: colors.accentGreen },
  closed: { bg: "#f0f0f0", color: "#666" },
};

export default function VetCasesListPage() {
  const router = useRouter();

  useEffect(() => {
    document.title = "Vet Cases \u2014 PashuRaksha ERP";
  }, []);

  const [tabIndex, setTabIndex] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(20);
  const [cases, setCases] = useState<VetCase[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const currentStatus = STATUS_TABS[tabIndex].value;

  const fetchCases = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const skip = page * rowsPerPage;
      const res = await fetch(
        `${API_URL}/vet/cases?status=${currentStatus}&skip=${skip}&limit=${rowsPerPage}`,
        { credentials: "include" }
      );
      if (!res.ok) throw new Error(`API error ${res.status}`);
      const body = await res.json();
      const data = Array.isArray(body) ? body : body.data ?? [];
      setCases(data);
      setTotal(body.total ?? data.length);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load cases");
      setCases([]);
    } finally {
      setIsLoading(false);
    }
  }, [currentStatus, page, rowsPerPage]);

  useEffect(() => {
    fetchCases();
  }, [fetchCases]);

  const handleTabChange = useCallback((_: React.SyntheticEvent, newIndex: number) => {
    setTabIndex(newIndex);
    setPage(0);
  }, []);

  const farmerName = useCallback((c: VetCase) => {
    return c.animal?.owner?.name ?? c.farmer?.name ?? "\u2014";
  }, []);

  const channelLabel = useCallback((ch: string) => {
    return ch.replace(/_/g, " ");
  }, []);

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ color: colors.text }}>
        Vet Cases
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        Review, diagnose, and manage veterinary consultations
      </Typography>

      <Paper>
        <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
          <Tabs
            value={tabIndex}
            onChange={handleTabChange}
            textColor="primary"
            indicatorColor="primary"
            sx={{
              px: 2,
              "& .MuiTab-root": {
                textTransform: "none",
                fontWeight: 600,
                fontSize: "13px",
                minHeight: 48,
              },
            }}
          >
            {STATUS_TABS.map((t) => (
              <Tab key={t.value} label={t.label} />
            ))}
          </Tabs>
        </Box>

        {isLoading ? (
          <Box sx={{ display: "flex", justifyContent: "center", p: 8 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Box sx={{ p: 4 }}>
            <Alert severity="error">{error}</Alert>
          </Box>
        ) : (
          <>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Farmer</TableCell>
                    <TableCell>Animal</TableCell>
                    <TableCell>Channel</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {cases.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} sx={{ border: 0 }}>
                        <EmptyState
                          title="No cases found"
                          subtitle={`No ${STATUS_TABS[tabIndex].label.toLowerCase()} cases at the moment.`}
                        />
                      </TableCell>
                    </TableRow>
                  ) : (
                    cases.map((c) => (
                      <TableRow
                        key={c.id}
                        hover
                        sx={{ cursor: "pointer" }}
                        onClick={() => router.push(`/vet/cases/${c.id}`)}
                      >
                        <TableCell sx={{ fontWeight: 500, color: colors.text, fontSize: "13px" }}>
                          {farmerName(c)}
                        </TableCell>
                        <TableCell>
                          {c.animal ? (
                            <SpeciesChip species={c.animal.species} />
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              {c.animal_id?.slice(0, 8)}
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={channelLabel(c.channel)}
                            size="small"
                            sx={{
                              bgcolor: channelConfig[c.channel]?.bg ?? colors.infoLight,
                              color: channelConfig[c.channel]?.color ?? colors.accentBlue,
                              fontWeight: 600,
                              fontSize: "11px",
                              textTransform: "capitalize",
                              border: "none",
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={c.priority}
                            size="small"
                            sx={{
                              bgcolor: priorityConfig[c.priority]?.bg ?? "#f0f0f0",
                              color: priorityConfig[c.priority]?.color ?? "#666",
                              fontWeight: 600,
                              fontSize: "11px",
                              textTransform: "capitalize",
                              border: "none",
                            }}
                          />
                        </TableCell>
                        <TableCell sx={{ ...sxCodeCell, whiteSpace: "nowrap" }}>
                          {fmtDate(c.created_at)}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={c.status.replace(/_/g, " ")}
                            size="small"
                            sx={{
                              bgcolor: statusConfig[c.status]?.bg ?? "#f0f0f0",
                              color: statusConfig[c.status]?.color ?? "#666",
                              fontWeight: 600,
                              fontSize: "11px",
                              textTransform: "capitalize",
                              border: "none",
                            }}
                          />
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              component="div"
              count={total}
              page={page}
              onPageChange={(_, p) => setPage(p)}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={(e) => {
                setRowsPerPage(parseInt(e.target.value, 10));
                setPage(0);
              }}
              rowsPerPageOptions={[10, 20, 50]}
            />
          </>
        )}
      </Paper>
    </Box>
  );
}
