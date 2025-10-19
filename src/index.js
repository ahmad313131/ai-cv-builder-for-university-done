import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import reportWebVitals from "./reportWebVitals";
import { ThemeProvider, CssBaseline } from "@mui/material";
import useThemeMode, { ThemeModeProvider } from "./hooks/useThemeMode";

function Root() {
  const { theme } = useThemeMode(); // من الكونتكست
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  // <React.StrictMode>
  <ThemeModeProvider>
    <Root />
  </ThemeModeProvider>
  // </React.StrictMode>
);

reportWebVitals();
