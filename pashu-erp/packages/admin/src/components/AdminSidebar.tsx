'use client';

import React, { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import {
  Box,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Avatar,
  Divider,
  Drawer,
  AppBar,
  Toolbar,
  IconButton,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PeopleIcon from '@mui/icons-material/People';
import PetsIcon from '@mui/icons-material/Pets';
import LocalDrinkIcon from '@mui/icons-material/LocalDrink';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import VaccinesIcon from '@mui/icons-material/Vaccines';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import StoreIcon from '@mui/icons-material/Store';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import SensorsIcon from '@mui/icons-material/Sensors';
import MapIcon from '@mui/icons-material/Map';
import AssignmentIcon from '@mui/icons-material/Assignment';
import MedicalServicesIcon from '@mui/icons-material/MedicalServices';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import { useGetIdentity } from '@refinedev/core';
import { colors } from '@/theme/theme';

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

interface UserIdentity {
  id: string;
  name: string;
  role?: string;
}

const adminNavSections: NavSection[] = [
  {
    title: 'CORE OPERATIONS',
    items: [
      { label: 'Dashboard', href: '/', icon: <DashboardIcon /> },
      { label: 'Farmers', href: '/farmers', icon: <PeopleIcon /> },
      { label: 'Animals', href: '/animals', icon: <PetsIcon /> },
      { label: 'Milk Collection', href: '/milk', icon: <LocalDrinkIcon /> },
      { label: 'Health Alerts', href: '/health', icon: <LocalHospitalIcon /> },
      { label: 'Vaccinations', href: '/vaccinations', icon: <VaccinesIcon /> },
    ],
  },
  {
    title: 'VETERINARY',
    items: [
      { label: 'Vet Dashboard', href: '/vet', icon: <MedicalServicesIcon /> },
      { label: 'Vet Cases', href: '/vet/cases', icon: <AssignmentIcon /> },
    ],
  },
  {
    title: 'LIVELIHOODS & SCHEMES',
    items: [
      { label: 'Govt Schemes', href: '/schemes', icon: <AccountBalanceIcon /> },
      { label: 'Marketplace', href: '/marketplace', icon: <StoreIcon /> },
      { label: 'Income Analytics', href: '/income', icon: <TrendingUpIcon /> },
    ],
  },
  {
    title: 'ANALYTICS & INSIGHTS',
    items: [
      { label: 'Map View', href: '/map', icon: <MapIcon /> },
    ],
  },
  {
    title: 'INTEGRATIONS',
    items: [
      { label: 'IoT Devices', href: '/iot', icon: <SensorsIcon /> },
    ],
  },
];

const vetNavSections: NavSection[] = [
  {
    title: 'VETERINARY',
    items: [
      { label: 'Vet Dashboard', href: '/vet', icon: <MedicalServicesIcon /> },
      { label: 'My Cases', href: '/vet/cases', icon: <AssignmentIcon /> },
      { label: 'District Alerts', href: '/vet/alerts', icon: <NotificationsActiveIcon /> },
    ],
  },
  {
    title: 'LOOKUP',
    items: [
      { label: 'Animals', href: '/animals', icon: <PetsIcon /> },
      { label: 'Vaccinations', href: '/vaccinations', icon: <VaccinesIcon /> },
      { label: 'Health Events', href: '/health', icon: <LocalHospitalIcon /> },
      { label: 'Map View', href: '/map', icon: <MapIcon /> },
    ],
  },
];

const SIDEBAR_WIDTH = 260;

function AdminSidebar() {
  const pathname = usePathname();
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up('lg'));
  const { data: identity } = useGetIdentity<UserIdentity>();
  const [role, setRole] = useState<string>('admin');
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    if (identity?.role) {
      setRole(identity.role);
    }
  }, [identity?.role]);

  // Close mobile drawer on navigation
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  const navSections = role === 'vet' ? vetNavSections : adminNavSections;
  const displayName = identity?.name ?? (role === 'vet' ? 'Veterinarian' : 'Admin');
  const displayRole = role === 'vet' ? 'District Veterinarian' : 'District Admin';

  const sidebarContent = (
    <Box
      role="navigation"
      aria-label="Main navigation"
      sx={{
        width: SIDEBAR_WIDTH,
        minWidth: SIDEBAR_WIDTH,
        height: '100vh',
        bgcolor: colors.sidebarBg,
        display: 'flex',
        flexDirection: 'column',
        overflowY: 'auto',
        overflowX: 'hidden',
        '&::-webkit-scrollbar': { width: 4 },
        '&::-webkit-scrollbar-thumb': {
          bgcolor: 'rgba(255,255,255,0.15)',
          borderRadius: 2,
        },
      }}
    >
      {/* Logo / Brand */}
      <Box sx={{ px: 2.5, py: 2.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            sx={{
              width: 36,
              height: 36,
              borderRadius: '10px',
              bgcolor: colors.sidebarActive,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <PetsIcon sx={{ color: 'common.white', fontSize: 22 }} />
          </Box>
          <Box>
            <Typography
              sx={{
                color: 'common.white',
                fontWeight: 700,
                fontSize: '16px',
                lineHeight: 1.2,
                letterSpacing: '-0.01em',
              }}
            >
              PashuRaksha
            </Typography>
            <Typography
              sx={{
                color: colors.sidebarText,
                fontSize: '11px',
                fontWeight: 500,
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
              }}
            >
              {role === 'vet' ? 'Vet Portal' : 'ERP Admin'}
            </Typography>
          </Box>
        </Box>
      </Box>

      <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)', mx: 2 }} />

      {/* Nav Sections */}
      <Box component="nav" aria-label="Main navigation" sx={{ flex: 1, py: 1 }}>
        {navSections.map((section) => (
          <Box key={section.title} sx={{ mb: 0.5 }}>
            <Typography
              sx={{
                px: 2.5,
                pt: 2,
                pb: 0.5,
                fontSize: '10px',
                fontWeight: 700,
                letterSpacing: '0.1em',
                color: 'rgba(200,221,216,0.72)',
                textTransform: 'uppercase',
              }}
            >
              {section.title}
            </Typography>
            <List dense disablePadding>
              {section.items.map((item) => {
                const isActive =
                  item.href === '/'
                    ? pathname === '/'
                    : pathname.startsWith(item.href);
                return (
                  <ListItemButton
                    key={item.href}
                    component={Link}
                    href={item.href}
                    sx={{
                      mx: 1,
                      mb: 0.25,
                      borderRadius: '8px',
                      py: 0.75,
                      px: 1.5,
                      borderLeft: isActive
                        ? `3px solid ${colors.sidebarActive}`
                        : '3px solid transparent',
                      bgcolor: isActive
                        ? 'rgba(22,160,133,0.12)'
                        : 'transparent',
                      '&:hover': {
                        bgcolor: isActive
                          ? 'rgba(22,160,133,0.18)'
                          : 'rgba(255,255,255,0.05)',
                      },
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <ListItemIcon
                      sx={{
                        minWidth: 32,
                        color: isActive
                          ? colors.sidebarActive
                          : colors.sidebarText,
                        '& .MuiSvgIcon-root': { fontSize: 20 },
                      }}
                    >
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText
                      primary={item.label}
                      primaryTypographyProps={{
                        fontSize: '13px',
                        fontWeight: isActive ? 600 : 400,
                        color: isActive ? 'common.white' : colors.sidebarText,
                      }}
                    />
                  </ListItemButton>
                );
              })}
            </List>
          </Box>
        ))}
      </Box>

      {/* User Footer */}
      <Divider sx={{ borderColor: 'rgba(255,255,255,0.08)', mx: 2 }} />
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Avatar
          sx={{
            width: 34,
            height: 34,
            bgcolor: colors.sidebarActive,
            fontSize: '13px',
            fontWeight: 600,
          }}
        >
          {displayName.charAt(0).toUpperCase()}
        </Avatar>
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography
            sx={{
              color: 'common.white',
              fontSize: '12.5px',
              fontWeight: 600,
              lineHeight: 1.2,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {displayName}
          </Typography>
          <Typography
            sx={{
              color: colors.sidebarText,
              fontSize: '10.5px',
              lineHeight: 1.2,
            }}
          >
            {displayRole}
          </Typography>
        </Box>
      </Box>
    </Box>
  );

  return (
    <>
      {!isDesktop && (
        <AppBar
          position="fixed"
          sx={{
            zIndex: theme.zIndex.drawer + 1,
            bgcolor: colors.sidebarBg,
          }}
        >
          <Toolbar>
            <IconButton
              color="inherit"
              edge="start"
              onClick={() => setMobileOpen(!mobileOpen)}
              aria-label="Toggle navigation menu"
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              PashuRaksha
            </Typography>
          </Toolbar>
        </AppBar>
      )}
      <Drawer
        variant={isDesktop ? 'permanent' : 'temporary'}
        open={isDesktop || mobileOpen}
        onClose={() => setMobileOpen(false)}
        sx={{
          width: SIDEBAR_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: SIDEBAR_WIDTH,
            boxSizing: 'border-box',
            border: 'none',
          },
        }}
      >
        {sidebarContent}
      </Drawer>
    </>
  );
}

export default React.memo(AdminSidebar);
export { SIDEBAR_WIDTH };
