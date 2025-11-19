// src/components/UserMenu.jsx
import { useEffect, useState } from "react";
import { Button, Stack, Typography } from "@mui/material";
import { me, logout } from "../api";
import { useNavigate } from "react-router-dom";

export default function UserMenu() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    me().then(setUser).catch(() => {});
  }, []);

  return (
    <Stack direction="row" spacing={2} alignItems="center">
      {user && <Typography variant="body2">Signed in as <b>{user?.username || user?.email}</b></Typography>}
      <Button
        size="small"
        variant="outlined"
        onClick={() => { logout(); navigate("/login", { replace: true }); }}
      >
        Logout
      </Button>
    </Stack>
  );
}
