// src/components/Header.jsx
import React, { useEffect, useState } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Divider,
  useMediaQuery,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import LoginIcon from "@mui/icons-material/Login";
import LogoutIcon from "@mui/icons-material/Logout";
import { NavLink, useNavigate } from "react-router-dom";
import ThemeToggle from "./ThemeToggle";
import { me, getToken, logout } from "../api";
import { useTheme } from "@mui/material/styles";

export default function Header() {
  const [user, setUser] = useState(null); // لعرض الإيميل إن توفّر
  const [anchorEl, setAnchorEl] = useState(null);
  const navigate = useNavigate();
  const theme = useTheme();
  const isMdUp = useMediaQuery(theme.breakpoints.up("md"));

  // ✅ التوكن هو المصدر الرئيسي لعرض زر Logout / My CVs
  const token = getToken();
  const authed = !!token;

  useEffect(() => {
    if (!authed) { setUser(null); return; }
    // حاول جب بيانات المستخدم — لو فشل، زر Logout يبقى ظاهر
    me().then(setUser).catch(() => setUser(null));
  }, [authed]);

  const goHome = () => navigate("/", { replace: true });
  const goLogin = () => navigate("/login?next=/builder");
  const handleLogout = () => {
    logout();
    setUser(null);
    goHome();
  };

  // ستايل الروابط (مع حالة active)
  const linkStyle = ({ isActive }) => ({
    textDecoration: "none",
    marginRight: 18,
    fontWeight: isActive ? 800 : 600,
    opacity: isActive ? 1 : 0.85,
    color: "inherit",
    padding: "6px 0",
    borderBottom: isActive ? "2px solid currentColor" : "2px solid transparent",
  });

  const openMenu = (e) => setAnchorEl(e.currentTarget);
  const closeMenu = () => setAnchorEl(null);
  const go = (path) => { closeMenu(); navigate(path); };

  return (
    <AppBar
      position="sticky"
      elevation={0}
      color="transparent"
      sx={{
        backdropFilter: "saturate(180%) blur(6px)",
        backgroundColor: (t) =>
          t.palette.mode === "dark" ? "rgba(18,18,18,0.6)" : "rgba(255,255,255,0.7)",
        borderBottom: (t) =>
          `1px solid ${t.palette.mode === "dark" ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)"}`,
      }}
    >
      <Toolbar sx={{ minHeight: 64, px: { xs: 2, sm: 3 } }}>
        {/* Brand */}
        <Typography
          variant="h6"
          fontWeight={800}
          sx={{ mr: 2, letterSpacing: 0.3, whiteSpace: "nowrap", cursor: "pointer" }}
          onClick={goHome}
        >
          AI CV Builder
        </Typography>

        <Box sx={{ flexGrow: 1 }} />

        {/* Desktop links */}
        {isMdUp && (
          <Box sx={{ display: "flex", alignItems: "center", mr: 1 }}>
            <NavLink to="/" style={linkStyle}>Home</NavLink>
            <NavLink to="/builder" style={linkStyle}>Builder</NavLink>
            {authed && <NavLink to="/cvs" style={linkStyle}>My CVs</NavLink>}
          </Box>
        )}

        {/* Theme toggle */}
        <Box sx={{ ml: { xs: 0.5, md: 1.5 } }}>
          <ThemeToggle />
        </Box>

        {/* Actions */}
        {isMdUp ? (
          // ===== Desktop =====
          <Box sx={{ ml: 1.5, display: "flex", alignItems: "center" }}>
            {authed ? (
              <>
                {/* عرض الإيميل فقط لو نجحت /me */}
                {user && (
                  <Typography
                    variant="body2"
                    sx={{
                      mr: 1.5,
                      maxWidth: { xs: 140, md: 220 },
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                      opacity: 0.9,
                    }}
                    title={user.email || user.username}
                  >
                    Signed in as <b>{user.username }</b>
                  </Typography>
                )}
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<LogoutIcon fontSize="small" />}
                  onClick={handleLogout}
                >
                  Logout
                </Button>
              </>
            ) : (
              <Button
                size="small"
                variant="contained"
                startIcon={<LoginIcon fontSize="small" />}
                onClick={goLogin}
              >
                Login
              </Button>
            )}
          </Box>
        ) : (
          // ===== Mobile: hamburger =====
          <Box sx={{ ml: 0.5 }}>
            <IconButton edge="end" onClick={openMenu} aria-label="menu">
              <MenuIcon />
            </IconButton>

           <Menu
  anchorEl={anchorEl}
  open={Boolean(anchorEl)}
  onClose={closeMenu}
  PaperProps={{ sx: { minWidth: 200 } }}
  anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
  transformOrigin={{ vertical: "top", horizontal: "right" }}
>
  {/* عناصر عامة */}
  <MenuItem onClick={() => go("/")}>Home</MenuItem>
  <MenuItem onClick={() => go("/builder")}>Builder</MenuItem>
  <Divider />

  {authed
    ? [
        // اختياري: عرض الإيميل/اليوزرنيم
        user && (
          <MenuItem key="signed" disabled title={user.username || user.email}>
            Signed in as {user?.username || user?.email}
          </MenuItem>
        ),
        // ✅ My CVs يظهر فقط للمستخدم المسجّل
        <MenuItem
          key="mycvs"
          onClick={() => {
            closeMenu();
            go("/cvs");
          }}
        >
          My CVs
        </MenuItem>,
        <Divider key="div2" />,
        <MenuItem
          key="logout"
          onClick={() => {
            closeMenu();
            handleLogout();
          }}
        >
          <LogoutIcon fontSize="small" style={{ marginRight: 8 }} />
          Logout
        </MenuItem>,
      ].filter(Boolean)
    : [
        <MenuItem
          key="login"
          onClick={() => {
            closeMenu();
            goLogin();
          }}
        >
          <LoginIcon fontSize="small" style={{ marginRight: 8 }} />
          Login
        </MenuItem>,
      ]}
</Menu>


          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
}
