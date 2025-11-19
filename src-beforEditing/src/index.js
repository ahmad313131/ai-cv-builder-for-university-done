// src/index.js
import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import reportWebVitals from "./reportWebVitals";
import { ThemeProvider, CssBaseline } from "@mui/material";
import useThemeMode, { ThemeModeProvider } from "./hooks/useThemeMode";
import AppRouter from "./AppRouter"; // <-- بدل App

function Root() {
  const { theme } = useThemeMode(); // من الكونتكست
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppRouter /> {/* <-- بدل <App /> */}
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
