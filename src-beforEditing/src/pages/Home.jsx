// src/pages/Home.jsx
import {
  Box,
  Container,
  Typography,
  Button,
  Stack,
  Chip,
  Paper,
  Divider,
} from "@mui/material";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import ThemeToggle from "../components/ThemeToggle";
import React, { useEffect, useState } from "react";
import { getToken, me } from "../api"; // ✅ جديد

export default function Home() {
  const navigate = useNavigate();

  // ✅ حالة الدخول مع جلب اختياري لبيانات المستخدم (لا يؤثر على الستايل)
  const [authed, setAuthed] = useState(!!getToken());
  const [user, setUser] = useState(null);

  useEffect(() => {
    const t = getToken();
    setAuthed(!!t);
    if (!t) { setUser(null); return; }
    me().then(setUser).catch(() => setUser(null));
  }, []);

  return (
    <Box
      sx={{
        minHeight: "100vh",
        py: { xs: 6, md: 10 },
        background: (theme) =>
          theme.palette.mode === "dark"
            ? "radial-gradient(1200px 600px at 20% -10%, rgba(99,102,241,.15), transparent), radial-gradient(900px 500px at 120% 10%, rgba(168,85,247,.12), transparent)"
            : "radial-gradient(1200px 600px at 20% -10%, rgba(99,102,241,.08), transparent), radial-gradient(900px 500px at 120% 10%, rgba(168,85,247,.08), transparent)",
      }}
    >

      <Container maxWidth="md">
        <Paper
          elevation={6}
          sx={{
            p: { xs: 3, md: 5 },
            borderRadius: 4,
            position: "relative",
            overflow: "hidden",
          }}
        >
          {/* Header */}
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              mb: { xs: 2, md: 3 },
            }}
          >
            <Typography variant="h5" fontWeight={800} sx={{ letterSpacing: 0.2 }}>
              AI CV Builder
            </Typography>
            <ThemeToggle />
          </Box>

          {/* Hero */}
          <Typography
            variant="h3"
            fontWeight={900}
            sx={{
              mb: 1,
              lineHeight: 1.1,
              letterSpacing: 0.3,
              background:
                "linear-gradient(90deg, #7c4dff 0%, #8ab4ff 60%, #22d3ee 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Build an ATS-friendly Resume in minutes
          </Typography>

          <Typography variant="h6" sx={{ opacity: 0.85, mb: 3 }}>
            Fill your info, paste a Job Description, analyze the match with an on-device LLM
            and our skill ontology, then download a polished PDF.
          </Typography>

          
           {/* welcome comment */}
          {user?.email && (
            <Typography variant="subtitle1" sx={{ mb: 1, opacity: 0.9 }}>
                Welcome back, <b>{user?.username || user?.email}</b> 👋
            </Typography>
            )}


          {/* Badges */}
          <Stack direction="row" spacing={1.25} sx={{ mb: 3, flexWrap: "wrap" }}>
            <Chip label="React + MUI" />
            <Chip label="FastAPI" />
            <Chip label="Ollama (optional)" />
            <Chip label="PDF Generator" />
            <Chip label="Skill Ontology" />
            <Chip label="Local-first" />
          </Stack>

          {/* CTA — نحافظ على نفس الستايل تمامًا */}
          {!authed ? (
            <Stack
              direction={{ xs: "column", sm: "row" }}
              spacing={2}
              sx={{ mb: 3 }}
            >
              <Button
                component={RouterLink}
                to="/login" // push (مش replace) لحتى يشتغل Back
                variant="contained"
                size="large"
                sx={{ borderRadius: 2, minWidth: 180 }}
              >
                Log in
              </Button>

              <Button
                component={RouterLink}
                to="/builder" // push افتراضيًا
                variant="outlined"
                size="large"
                sx={{ borderRadius: 2, minWidth: 220 }}
              >
                Continue without login
              </Button>
            </Stack>
          ) : (
            <Stack
              direction={{ xs: "column", sm: "row" }}
              spacing={2}
              sx={{ mb: 3 }}
            >
              <Button
                component={RouterLink}
                to="/builder"
                variant="contained"
                size="large"
                sx={{ borderRadius: 2, minWidth: 180 }}
              >
                Open Builder
              </Button>

              <Button
                component={RouterLink}
                to="/cvs"
                variant="outlined"
                size="large"
                sx={{ borderRadius: 2, minWidth: 220 }}
              >
                My CVs
              </Button>
            </Stack>
          )}

          <Divider sx={{ my: 3 }} />

          {/* How it works */}
          <Box sx={{ mt: 1 }}>
            <Typography variant="subtitle1" fontWeight={800} gutterBottom>
              How it works
            </Typography>
            <ol style={{ marginTop: 0, paddingLeft: "1.2rem", lineHeight: 1.8 }}>
              <li>Enter personal info, education, experience, and skills.</li>
              <li>
                Paste a Job Description and click <em>Analyze (AI)</em> or <em>Fast Analyze</em>.
              </li>
              <li>Review the match score, reasons, missing skills, and nice-to-have.</li>
              <li>Download a clean, ATS-friendly PDF resume.</li>
            </ol>
          </Box>

          {/* Footer mini actions */}
          <Stack
            direction="row"
            spacing={1.5}
            sx={{ mt: 2, justifyContent: "flex-end", flexWrap: "wrap" }}
          >
            <Button variant="text" onClick={() => navigate("/builder")}>
              Skip & start building →
            </Button>
          </Stack>

          {/* <Button variant="contained" onClick={() => navigate("/builder")}>
            Start Building
          </Button> */}
        </Paper>
      </Container>
    </Box>
  );
}
