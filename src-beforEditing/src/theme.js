import { createTheme, responsiveFontSizes } from "@mui/material/styles";

const base = {
  shape: { borderRadius: 16 },
  typography: {
    fontFamily: `'Inter', system-ui, -apple-system, Segoe UI, Roboto, Arial, "Apple Color Emoji", "Segoe UI Emoji"`,
    h4: { fontWeight: 700 },
    button: { textTransform: "none", fontWeight: 600 },
  },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: {
        root: { borderRadius: 14, paddingInline: 18, paddingBlock: 10 },
      },
    },
    MuiCard: { styleOverrides: { root: { borderRadius: 20 } } },
    MuiPaper: { styleOverrides: { root: { borderRadius: 20 } } },
    MuiTooltip: { defaultProps: { arrow: true } },
  },
};

const lightTokens = {
  palette: {
    mode: "light",
    primary: { main: "#6E59F7" }, // بنفسجي عصري
    success: { main: "#22C55E" },
    info: { main: "#3B82F6" },
    secondary: { main: "#64748B" }, // slate
    background: { default: "#F7F8FB", paper: "#FFFFFF" },
  },
};

const darkTokens = {
  palette: {
    mode: "dark",
    primary: { main: "#8B7BFF" },
    success: { main: "#34D399" },
    info: { main: "#60A5FA" },
    secondary: { main: "#94A3B8" },
    background: { default: "#0B0F17", paper: "#111827" },
  },
};

export function makeTheme(mode = "light") {
  const tokens = mode === "dark" ? darkTokens : lightTokens;
  return responsiveFontSizes(createTheme({ ...base, ...tokens }));
}
