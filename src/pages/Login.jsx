// src/pages/Login.jsx
import React, { useState } from "react";
import { TextField, Button, Typography, Stack, Alert, Link } from "@mui/material";
import { useNavigate, useSearchParams } from "react-router-dom";
import { login, register as apiRegister, me } from "../api";

export default function Login() {
  const [mode, setMode] = useState("login"); // "login" | "register"
  // حقول login
  const [identifier, setIdentifier] = useState(""); // Email OR Username
  // حقول register
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  // مشترك
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [sp] = useSearchParams();
  const next = sp.get("next") || "/builder";

  async function handleSubmit(e) {
    e.preventDefault();
    setErr("");
    setLoading(true);
    try {
      if (mode === "register") {
        // إنشاء حساب: نرسل ايميل + يوزرنيم + كلمة السر
        await apiRegister(email, password, username);
        // بعد الإنشاء مباشرة نسجّل دخول بأي من الحقلين (بنستعمل الإيميل هنا)
        await login(email, password);
      } else {
        // تسجيل دخول: حقل واحد فقط (identifier) = Email أو Username
        await login(identifier, password);
      }
      await me(); // تأكيد التوكن
      navigate(next, { replace: true });
    } catch (e) {
      setErr(e.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: 440, margin: "64px auto" }}>
      <Stack spacing={2}>
        <Typography variant="h4" fontWeight={800}>
          {mode === "login" ? "Sign in" : "Create account"}
        </Typography>

        {err ? <Alert severity="error">{err}</Alert> : null}

        {mode === "login" ? (
          <>
            <TextField
              label="Email or Username"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              required
              fullWidth
              autoFocus
            />
            <TextField
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              fullWidth
            />
          </>
        ) : (
          <>
            <TextField
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              fullWidth
              autoFocus
            />
            <TextField
              label="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              helperText="3–30 chars: a-z, 0-9, dot, underscore, dash"
              required
              fullWidth
              inputProps={{ maxLength: 30 }}
            />
            <TextField
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              fullWidth
            />
          </>
        )}

        <Button type="submit" variant="contained" disabled={loading} size="large">
          {loading ? "Please wait..." : mode === "login" ? "Sign in" : "Sign up"}
        </Button>

        <Typography variant="body2" sx={{ textAlign: "center" }}>
          {mode === "login" ? (
            <>
              Don’t have an account?{" "}
              <Link component="button" onClick={() => setMode("register")}>
                Create one
              </Link>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <Link component="button" onClick={() => setMode("login")}>
                Sign in
              </Link>
            </>
          )}
        </Typography>

        {/* زر رجوع خفيف اختياري */}
        <Button variant="text" onClick={() => navigate("/", { replace: true })}>
          ← Back to Home
        </Button>
      </Stack>
    </form>
  );
}
