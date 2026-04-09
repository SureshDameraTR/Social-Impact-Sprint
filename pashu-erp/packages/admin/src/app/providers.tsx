"use client";

import { Refine, Authenticated } from "@refinedev/core";
import routerProvider from "@refinedev/nextjs-router";
import { usePathname } from "next/navigation";
import { ThemeProvider, CssBaseline, Box, CircularProgress } from "@mui/material";
import DashboardIcon from "@mui/icons-material/Dashboard";
import PeopleIcon from "@mui/icons-material/People";
import PetsIcon from "@mui/icons-material/Pets";
import LocalDrinkIcon from "@mui/icons-material/LocalDrink";
import LocalHospitalIcon from "@mui/icons-material/LocalHospital";
import VaccinesIcon from "@mui/icons-material/Vaccines";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import StoreIcon from "@mui/icons-material/Store";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import SensorsIcon from "@mui/icons-material/Sensors";
import MapIcon from "@mui/icons-material/Map";

import { authProvider } from "@/providers/auth-provider";
import { restDataProvider } from "@/providers/data-provider";
import { adminTheme } from "@/theme/theme";
import EmotionCacheProvider from "@/theme/EmotionCache";
import AdminSidebar, { SIDEBAR_WIDTH } from "@/components/AdminSidebar";

function AuthenticatedLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  if (pathname === "/login") {
    return <>{children}</>;
  }

  return (
    <Authenticated
      key="auth-guard"
      redirectOnFail="/login"
      loading={
        <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
          <CircularProgress />
        </Box>
      }
    >
      <Box sx={{ display: "flex", minHeight: "100vh" }}>
        <Box component="nav" aria-label="Primary navigation">
          <AdminSidebar />
        </Box>
        <Box
          component="main"
          role="main"
          id="main-content"
          sx={{
            flexGrow: 1,
            ml: `${SIDEBAR_WIDTH}px`,
            minHeight: "100vh",
            bgcolor: "background.default",
          }}
        >
          {children}
        </Box>
      </Box>
    </Authenticated>
  );
}

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <EmotionCacheProvider>
    <ThemeProvider theme={adminTheme}>
      <CssBaseline />
      <Refine
        routerProvider={routerProvider}
        dataProvider={restDataProvider}
        authProvider={authProvider}
        resources={[
          {
            name: "dashboard",
            list: "/",
            meta: { label: "Dashboard", icon: <DashboardIcon /> },
          },
          {
            name: "farmers",
            list: "/farmers",
            meta: { label: "Farmers", icon: <PeopleIcon /> },
          },
          {
            name: "animals",
            list: "/animals",
            meta: { label: "Animals", icon: <PetsIcon /> },
          },
          {
            name: "milk",
            list: "/milk",
            meta: { label: "Milk Collection", icon: <LocalDrinkIcon /> },
          },
          {
            name: "health",
            list: "/health",
            meta: { label: "Health Alerts", icon: <LocalHospitalIcon /> },
          },
          {
            name: "vaccinations",
            list: "/vaccinations",
            meta: { label: "Vaccinations", icon: <VaccinesIcon /> },
          },
          {
            name: "schemes",
            list: "/schemes",
            meta: { label: "Govt Schemes", icon: <AccountBalanceIcon /> },
          },
          {
            name: "marketplace",
            list: "/marketplace",
            meta: { label: "Marketplace", icon: <StoreIcon /> },
          },
          {
            name: "income",
            list: "/income",
            meta: { label: "Income Analytics", icon: <TrendingUpIcon /> },
          },
          {
            name: "iot",
            list: "/iot",
            meta: { label: "IoT Devices", icon: <SensorsIcon /> },
          },
          {
            name: "map",
            list: "/map",
            meta: { label: "Map View", icon: <MapIcon /> },
          },
        ]}
        options={{
          syncWithLocation: true,
          warnWhenUnsavedChanges: true,
        }}
      >
        <AuthenticatedLayout>{children}</AuthenticatedLayout>
      </Refine>
    </ThemeProvider>
    </EmotionCacheProvider>
  );
}
