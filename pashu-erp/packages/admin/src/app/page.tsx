"use client";

import { useEffect } from "react";
import { useList } from "@refinedev/core";
import { Box, Grid, Typography, Paper, CircularProgress, Alert } from "@mui/material";
import PeopleIcon from "@mui/icons-material/People";
import PetsIcon from "@mui/icons-material/Pets";
import LocalDrinkIcon from "@mui/icons-material/LocalDrink";
import WarningIcon from "@mui/icons-material/Warning";
import StoreIcon from "@mui/icons-material/Store";
import StorefrontIcon from "@mui/icons-material/Storefront";
import WomanIcon from "@mui/icons-material/Woman";
import AccountBalanceWalletIcon from "@mui/icons-material/AccountBalanceWallet";
import GroupsIcon from "@mui/icons-material/Groups";
import dynamic from "next/dynamic";
import { Skeleton } from "@mui/material";
import StatCard from "@/components/StatCard";
import GISMap, { MapPoint } from "@/components/GISMap";
import { colors, tooltipStyle, axisTickStyle, gridStroke } from "@/theme/theme";

interface MilkChartPoint {
  date: string;
  liters: number;
  farmers: number;
}

/* Lazy-loaded chart component to reduce initial bundle */
function DashboardChart({ data }: { data: MilkChartPoint[] }) {
  const {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Legend,
  } = require("recharts");

  return (
    <ResponsiveContainer width="100%" height={320}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="morningGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={colors.primary} stopOpacity={0.2} />
            <stop offset="95%" stopColor={colors.primary} stopOpacity={0.02} />
          </linearGradient>
          <linearGradient id="eveningGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={colors.accentBlue} stopOpacity={0.2} />
            <stop offset="95%" stopColor={colors.accentBlue} stopOpacity={0.02} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
        <XAxis
          dataKey="date"
          tick={axisTickStyle}
          axisLine={{ stroke: 'rgba(0,0,0,0.08)' }}
          tickLine={false}
        />
        <YAxis
          tick={axisTickStyle}
          axisLine={{ stroke: 'rgba(0,0,0,0.08)' }}
          tickLine={false}
        />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Area
          type="monotone"
          dataKey="liters"
          stroke={colors.primary}
          strokeWidth={2}
          fill="url(#morningGrad)"
          name="Total (L)"
          dot={false}
          activeDot={{ r: 4, strokeWidth: 2 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

const DashboardChartLazy = dynamic(() => Promise.resolve(DashboardChart), {
  ssr: false,
  loading: () => <Skeleton variant="rectangular" height={320} />,
});

interface DashboardStats {
  farmer_count: number;
  animal_count: number;
  todays_milk_liters: number;
  active_alerts: number;
  marketplace_revenue: number;
  active_sellers: number;
  women_farmers: number;
  women_revenue: number;
  women_animals: number;
  women_shg_count: number;
}

export default function DashboardPage() {
  useEffect(() => {
    document.title = 'Dashboard — PashuRaksha ERP';
  }, []);

  const { data: statsData, isLoading: statsLoading } = useList<DashboardStats>({ resource: "admin/stats" });
  const { data: milkListData, isLoading: milkLoading } = useList<MilkChartPoint>({ resource: "milk/daily-summary" });
  const { data: alertListData, isLoading: alertsLoading } = useList<MapPoint>({ resource: "health/alerts/map" });

  const stats = statsData?.data?.[0];
  const milkData: MilkChartPoint[] = milkListData?.data ?? [];
  const alertPoints: MapPoint[] = alertListData?.data ?? [];

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom sx={{ color: colors.text }}>
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" mb={3}>
        PashuRaksha ERP overview for Mysuru District
      </Typography>

      {/* Stat Cards - 3x2 grid */}
      <Grid container spacing={2.5} mb={4}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<PeopleIcon sx={{ fontSize: 28, color: colors.primary }} />}
            title="Total Farmers"
            value={statsLoading ? "\u2014" : stats?.farmer_count?.toLocaleString() ?? "\u2014"}
            color={colors.primary}
            trend={{ value: 12, label: "this month" }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<PetsIcon sx={{ fontSize: 28, color: colors.accentGreen }} />}
            title="Registered Animals"
            value={statsLoading ? "\u2014" : stats?.animal_count?.toLocaleString() ?? "\u2014"}
            color={colors.accentGreen}
            trend={{ value: 8, label: "this month" }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<LocalDrinkIcon sx={{ fontSize: 28, color: colors.accentBlue }} />}
            title="Today's Milk Collection"
            value={statsLoading ? "\u2014" : stats?.todays_milk_liters != null ? `${stats.todays_milk_liters.toLocaleString()} L` : "\u2014"}
            color={colors.accentBlue}
            trend={{ value: 5, label: "vs yesterday" }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<WarningIcon sx={{ fontSize: 28, color: colors.accentRed }} />}
            title="Active Health Alerts"
            value={statsLoading ? "\u2014" : stats?.active_alerts?.toLocaleString() ?? "\u2014"}
            color={colors.accentRed}
            trend={{ value: -15, label: "this week" }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<StoreIcon sx={{ fontSize: 28, color: colors.secondary }} />}
            title="Marketplace Revenue"
            value={statsLoading ? "\u2014" : stats?.marketplace_revenue != null ? `\u20B9${(stats.marketplace_revenue / 100000).toFixed(1)}L` : "\u2014"}
            color={colors.secondary}
            trend={{ value: 22, label: "this month" }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<StorefrontIcon sx={{ fontSize: 28, color: colors.accentAmber }} />}
            title="Active Sellers"
            value={statsLoading ? "\u2014" : stats?.active_sellers?.toLocaleString() ?? "\u2014"}
            color={colors.accentAmber}
            trend={{ value: 9, label: "this month" }}
          />
        </Grid>
      </Grid>

      {/* Women Empowerment Section */}
      <Typography variant="h5" gutterBottom sx={{ color: colors.primary, mt: 1 }}>
        Women Empowerment
      </Typography>
      <Typography variant="body2" color="text.secondary" mb={2}>
        Gender-disaggregated metrics for women farmer participation and economic impact
      </Typography>
      <Grid container spacing={2.5} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<WomanIcon sx={{ fontSize: 28, color: colors.accentGreen }} />}
            title="Women Farmers"
            value={
              statsLoading
                ? "\u2014"
                : stats?.women_farmers != null
                  ? `${stats.women_farmers} (${stats.farmer_count ? Math.round((stats.women_farmers / stats.farmer_count) * 100) : 0}%)`
                  : "\u2014"
            }
            color={colors.accentGreen}
            trend={{ value: 18, label: "this quarter" }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<AccountBalanceWalletIcon sx={{ fontSize: 28, color: colors.primary }} />}
            title="Women's Revenue"
            value={
              statsLoading
                ? "\u2014"
                : stats?.women_revenue != null
                  ? `\u20B9${stats.women_revenue.toLocaleString()}`
                  : "\u2014"
            }
            color={colors.primary}
            trend={{ value: 25, label: "this quarter" }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<PetsIcon sx={{ fontSize: 28, color: colors.accentAmber }} />}
            title="Women's Livestock"
            value={
              statsLoading
                ? "\u2014"
                : stats?.women_animals != null
                  ? `${stats.women_animals} (${stats.animal_count ? Math.round((stats.women_animals / stats.animal_count) * 100) : 0}%)`
                  : "\u2014"
            }
            color={colors.accentAmber}
            trend={{ value: 12, label: "this quarter" }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<GroupsIcon sx={{ fontSize: 28, color: colors.secondary }} />}
            title="SHG Groups"
            value={statsLoading ? "\u2014" : stats?.women_shg_count?.toLocaleString() ?? "\u2014"}
            color={colors.secondary}
            trend={{ value: 5, label: "this quarter" }}
          />
        </Grid>
      </Grid>

      {/* Charts and Map Row */}
      <Grid container spacing={2.5}>
        {/* Milk Collection Chart - Area chart with gradient */}
        <Grid item xs={12} lg={7}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom id="milk-chart-title">
              Milk Collection (Last 30 Days)
            </Typography>
            <Box
              role="img"
              aria-labelledby="milk-chart-title"
              aria-describedby="milk-chart-desc"
            >
              <DashboardChartLazy data={milkData} />
            </Box>
            <Box
              id="milk-chart-desc"
              component="p"
              sx={{ position: 'absolute', width: 1, height: 1, overflow: 'hidden', margin: 0, padding: 0 }}
            >
              Area chart showing milk collection over the last 30 days. Morning and evening sessions tracked separately.
            </Box>
          </Paper>
        </Grid>

        {/* Disease Alert Map */}
        <Grid item xs={12} lg={5}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom id="map-title">
              Disease Alert Map
            </Typography>
            <Box role="img" aria-labelledby="map-title" aria-describedby="map-desc">
              <GISMap
                center={[12.3, 76.6]}
                zoom={7}
                points={alertPoints}
                height={320}
              />
            </Box>
            <Box
              id="map-desc"
              component="p"
              sx={{ position: 'absolute', width: 1, height: 1, overflow: 'hidden', margin: 0, padding: 0 }}
            >
              Map showing disease alert locations across Karnataka. {alertPoints.length} active alerts.
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
