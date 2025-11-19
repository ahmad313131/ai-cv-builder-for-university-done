// src/components/AppLayout.jsx
import React from "react";
import { Outlet } from "react-router-dom";
import Header from "./Header";
import { Container } from "@mui/material";

export default function AppLayout() {
  return (
    <>
      <Header />
      <Container maxWidth="lg" sx={{ py: 3 }}>
        <Outlet />
      </Container>
    </>
  );
}
