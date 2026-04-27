"use client";

import { useEffect, useState } from "react";
import { useList } from "@refinedev/core";
import Link from "next/link";
import {
  Alert,
  Box,
  Grid,
  Typography,
  Paper,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Chip,
  Button,
  Skeleton,
} from "@mui/material";
import AssignmentIcon from "@mui/icons-material/Assignment";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import PetsIcon from "@mui/icons-material/Pets";
import WarningIcon from "@mui/icons-material/Warning";
import StatCard from "@/components/StatCard";
import GISMap, { MapPoint } from "@/components/GISMap";
import { colors } from "@/theme/theme";

interface VetDashboardStats {
  pending_cases: number;
  diagnosed_today: number;
  district_animals: number;
  active_alerts: number;
}

interface VetCase {
  id: string;
  farmer_name: string;
  animal_tag: string;
  priority: "critical" | "high" | "medium" | "low";
  channel: string;
  created_at: string;
}

const priorityColor: Record<string, string> = {
  critical: colors.accentRed,
  high: colors.accentAmber,
  medium: colors.accentBlue,
  low: colors.accentGreen,
};

const priorityBg: Record<string, string> = {
  critical: colors.errorLight,
  high: colors.warningLight,
  medium: colors.infoLight,
  low: colors.successLight,
};

export default function VetDashboardPage() {
  const { data: statsData, isLoading: statsLoading, isError: statsError } =
    useList<VetDashboardStats>({ resource: "vet/dashboard/stats" });
  const { data: casesData, isLoading: casesLoading, isError: casesError } = useList<VetCase>({
    resource: "vet/cases",
    filters: [{ field: "status", operator: "eq", value: "pending" }],
    pagination: { current: 1, pageSize: 10 },
  });
  const { data: alertMapData, isLoading: alertsLoading, isError: alertsError } = useList<MapPoint>({
    resource: "health/alerts/map",
  });

  const stats = statsData?.data?.[0];
  const cases: VetCase[] = casesData?.data ?? [];
  const alertPoints: MapPoint[] = alertMapData?.data ?? [];

  const hasError = statsError || casesError || alertsError;

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ color: colors.text }}>
        Vet Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        Veterinary case management and district overview
      </Typography>
      {hasError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Some dashboard data failed to load. Displayed values may be incomplete.
        </Alert>
      )}

      {/* Stat Cards */}
      <Grid container spacing={2.5} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={
              <AssignmentIcon sx={{ fontSize: 28, color: colors.accentAmber }} />
            }
            title="Pending Cases"
            value={
              statsLoading
                ? "\u2014"
                : stats?.pending_cases?.toLocaleString() ?? "\u2014"
            }
            color={colors.accentAmber}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={
              <CheckCircleIcon
                sx={{ fontSize: 28, color: colors.accentGreen }}
              />
            }
            title="Diagnosed Today"
            value={
              statsLoading
                ? "\u2014"
                : stats?.diagnosed_today?.toLocaleString() ?? "\u2014"
            }
            color={colors.accentGreen}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<PetsIcon sx={{ fontSize: 28, color: colors.accentBlue }} />}
            title="Animals in District"
            value={
              statsLoading
                ? "\u2014"
                : stats?.district_animals?.toLocaleString() ?? "\u2014"
            }
            color={colors.accentBlue}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<WarningIcon sx={{ fontSize: 28, color: colors.accentRed }} />}
            title="Active Alerts"
            value={
              statsLoading
                ? "\u2014"
                : stats?.active_alerts?.toLocaleString() ?? "\u2014"
            }
            color={colors.accentRed}
          />
        </Grid>
      </Grid>

      {/* Cases Table + District Map */}
      <Grid container spacing={2.5}>
        {/* Unassigned Cases Table */}
        <Grid item xs={12} lg={7}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom id="cases-table-title">
              Unassigned Cases
            </Typography>
            {casesLoading ? (
              <Box>
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} height={48} sx={{ mb: 0.5 }} />
                ))}
              </Box>
            ) : cases.length === 0 ? (
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ py: 4, textAlign: "center" }}
              >
                No pending cases at the moment.
              </Typography>
            ) : (
              <Table
                size="small"
                aria-labelledby="cases-table-title"
                sx={{ mt: 1 }}
              >
                <TableHead>
                  <TableRow>
                    <TableCell>Farmer</TableCell>
                    <TableCell>Animal</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Channel</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell align="right">Action</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {cases.map((c) => (
                    <TableRow key={c.id}>
                      <TableCell sx={{ fontWeight: 500, color: colors.text }}>
                        {c.farmer_name}
                      </TableCell>
                      <TableCell sx={{ color: colors.textDim }}>
                        {c.animal_tag}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={c.priority}
                          size="small"
                          sx={{
                            bgcolor: priorityBg[c.priority] ?? colors.infoLight,
                            color:
                              priorityColor[c.priority] ?? colors.accentBlue,
                            fontWeight: 600,
                            fontSize: "11px",
                            textTransform: "capitalize",
                          }}
                        />
                      </TableCell>
                      <TableCell sx={{ color: colors.textDim }}>
                        {c.channel}
                      </TableCell>
                      <TableCell sx={{ color: colors.textDim }}>
                        {new Date(c.created_at).toLocaleDateString("en-IN", {
                          day: "2-digit",
                          month: "short",
                        })}
                      </TableCell>
                      <TableCell align="right">
                        <Button
                          component={Link}
                          href={`/vet/cases/${c.id}`}
                          size="small"
                          variant="outlined"
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
                          Claim
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </Paper>
        </Grid>

        {/* District Alert Map */}
        <Grid item xs={12} lg={5}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom id="vet-map-title">
              District Alert Map
            </Typography>
            <Box
              role="img"
              aria-labelledby="vet-map-title"
              aria-describedby="vet-map-desc"
            >
              <GISMap
                center={[12.3, 76.6]}
                zoom={9}
                points={alertPoints}
                height={380}
              />
            </Box>
            <Box
              id="vet-map-desc"
              component="p"
              sx={{
                position: "absolute",
                width: 1,
                height: 1,
                overflow: "hidden",
                margin: 0,
                padding: 0,
              }}
            >
              Map showing disease alert locations in the district.{" "}
              {alertPoints.length} active alerts.
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
