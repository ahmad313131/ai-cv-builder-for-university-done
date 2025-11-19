import { IconButton, Tooltip } from "@mui/material";
import DarkModeRoundedIcon from "@mui/icons-material/DarkModeRounded";
import LightModeRoundedIcon from "@mui/icons-material/LightModeRounded";
import useThemeMode from "../hooks/useThemeMode";

export default function ThemeToggle() {
  const { mode, toggle } = useThemeMode();
  const isDark = mode === "dark";
  return (
    <Tooltip title={isDark ? "Switch to light" : "Switch to dark"}>
      <IconButton onClick={toggle} color="primary" sx={{ ml: 1 }}>
        {isDark ? <LightModeRoundedIcon /> : <DarkModeRoundedIcon />}
      </IconButton>
    </Tooltip>
  );
}
