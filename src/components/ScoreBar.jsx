import React from "react";
import { Box, LinearProgress, Typography } from "@mui/material";

/**
 * ScoreBar
 * props:
 *  - value: number (0..100)
 *  - height: number (px)
 */
export default function ScoreBar({ value = 0, height = 12 }) {
  const v = Math.max(0, Math.min(100, Number(value) || 0));
  const hue = (v / 100) * 120;            // 0..120 (red→green)
  const bar = `hsl(${hue} 85% 45%)`;

  return (
    <Box>
      <Box sx={{ display: "flex", alignItems: "baseline", mb: 0.5 }}>
        <Typography variant="subtitle2" sx={{ flex: 1 }}>
          Matching Score
        </Typography>
        <Typography variant="body2" sx={{ color: "text.secondary" }}>
          {v}%
        </Typography>
      </Box>

      <LinearProgress
        variant="determinate"
        value={v}
        sx={{
          height,
          borderRadius: 999,
          backgroundColor: (t) => (t.palette.mode === "dark" ? "#1F2937" : "#E5E7EB"),
          "& .MuiLinearProgress-bar": {
            borderRadius: 999,
            backgroundColor: bar,
          },
        }}
      />
    </Box>
  );
}