import { useNavigate, useLocation } from "react-router-dom";
import {
  AppBar,
  Toolbar,
  Typography,
  Tabs,
  Tab,
  IconButton,
  Box,
  Tooltip,
} from "@mui/material";
import LogoutOutlined from "@mui/icons-material/LogoutOutlined";
import { useAuth } from "../hooks/useAuth";
import { useCentre } from "../hooks/useCentre";

const NAV_TABS = [
  { label: "Intake", path: "/intake" },
  { label: "Dashboard", path: "/dashboard" },
  { label: "Settlements", path: "/settlements" },
];

export default function NavBar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const { centreName } = useCentre();

  const currentTab = NAV_TABS.findIndex((t) => location.pathname.startsWith(t.path));

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <AppBar position="sticky" sx={{ bgcolor: "#0d6b58" }}>
      <Toolbar sx={{ gap: 2 }}>
        <Box sx={{ minWidth: 180 }}>
          <Typography variant="subtitle1" fontWeight={700}>
            PashuRaksha
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.8 }}>
            {centreName || "Select Centre"}
          </Typography>
        </Box>

        <Tabs
          value={currentTab === -1 ? false : currentTab}
          onChange={(_, idx) => navigate(NAV_TABS[idx].path)}
          textColor="inherit"
          TabIndicatorProps={{ sx: { bgcolor: "#fff", height: 3 } }}
          sx={{ flexGrow: 1, ml: 2 }}
        >
          {NAV_TABS.map((tab) => (
            <Tab
              key={tab.path}
              label={tab.label}
              sx={{ color: "#fff", fontWeight: 600, textTransform: "none" }}
            />
          ))}
        </Tabs>

        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            {user?.name}
          </Typography>
          <Tooltip title="Logout">
            <IconButton color="inherit" onClick={handleLogout} size="small">
              <LogoutOutlined />
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
