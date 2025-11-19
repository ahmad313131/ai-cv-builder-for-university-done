// src/pages/MyCVs.jsx
import { useEffect, useState } from "react";
import { listCVs, downloadCV , getCV } from "../api";
import {
  Typography, Paper, List, ListItem, ListItemText, IconButton, Stack, Alert, CircularProgress
} from "@mui/material";
import PictureAsPdfRoundedIcon from "@mui/icons-material/PictureAsPdfRounded";

export default function MyCVs() {
  const [items, setItems] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    listCVs().then(setItems).catch(e => setErr(e.message || "Error"));
  }, []);

  if (err) return <Alert severity="error">{err}</Alert>;
  if (!items) return <CircularProgress />;

  return (
    <Paper sx={{ p: 3, borderRadius: 3 }}>
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5" fontWeight={800}>My CVs</Typography>
      </Stack>
      {items.length === 0 ? (
        <Typography color="text.secondary">No saved CVs yet.</Typography>
      ) : (
        <List>
          {items.map(cv => (
            <ListItem
              key={cv.id}
              secondaryAction={
                <IconButton
                edge="end"
                aria-label="pdf"
                onClick={async () => {
                try {
                    const full = await getCV(cv.id);
                    const filename = `cv_${cv.id}_${(full.name || "cv").replace(/\s+/g,"_")}.pdf`;
                    await downloadCV(full, filename);
                } catch (e) {
                    console.error(e);
                    setErr(e.message || "Failed to generate PDF");
                }
                }}

                                >
                <PictureAsPdfRoundedIcon />
                </IconButton>
              }
            >
              <ListItemText
                primary={cv.name || "(Unnamed CV)"}
                secondary={`${cv.email} • ${cv.created_at?.replace('T',' ').replace('Z','') || ''}`}
              />
            </ListItem>
          ))}
        </List>
      )}
    </Paper>
  );
}
