"use client";

import { Refine } from "@refinedev/core";
import routerProvider from "@refinedev/nextjs-router";
import { RefineThemes, ThemedLayoutV2, ThemedTitleV2 } from "@refinedev/mui";
import { ThemeProvider, CssBaseline } from "@mui/material";
import DashboardIcon from "@mui/icons-material/Dashboard";
import PeopleIcon from "@mui/icons-material/People";
import PetsIcon from "@mui/icons-material/Pets";
import LocalDrinkIcon from "@mui/icons-material/LocalDrink";
import LocalHospitalIcon from "@mui/icons-material/LocalHospital";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import StoreIcon from "@mui/icons-material/Store";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import SensorsIcon from "@mui/icons-material/Sensors";
import MapIcon from "@mui/icons-material/Map";

import { authProvider } from "@/providers/auth-provider";
import { restDataProvider } from "@/providers/data-provider";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <title>PashuRaksha ERP - Admin Dashboard</title>
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          crossOrigin=""
        />
      </head>
      <body>
        <ThemeProvider theme={RefineThemes.Blue}>
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
            <ThemedLayoutV2
              Title={({ collapsed }) => (
                <ThemedTitleV2
                  collapsed={collapsed}
                  text="PashuRaksha ERP"
                  icon={<PetsIcon />}
                />
              )}
            >
              {children}
            </ThemedLayoutV2>
          </Refine>
        </ThemeProvider>
      </body>
    </html>
  );
}
