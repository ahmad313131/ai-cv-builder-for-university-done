// src/components/AnalysisCard.jsx
import { Card, CardContent, Typography, Box, Chip } from "@mui/material";
import ScoreCircle from "./ScoreCircle";

export default function AnalysisCard({ analysis, analyzeError }) {
  if (analyzeError) {
    return (
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography color="error" variant="body1">
            {analyzeError}
          </Typography>
        </CardContent>
      </Card>
    );
  }
  if (!analysis) return null;

  const hasFast = Array.isArray(analysis.suggestions);
  const hasLLM =
    Array.isArray(analysis.reasons) || Array.isArray(analysis.missing_skills);

  const score = Number(analysis?.matching_score ?? 0);
  const level =
    analysis?.match_level ||
    (score >= 70 ? "Strong Match" : score >= 40 ? "Medium Match" : "Weak Match");

  const chipColor =
    level === "Strong Match" ? "success" : level === "Medium Match" ? "warning" : "error";

  return (
    <Card sx={{ mt: 4 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Analysis Result
        </Typography>

        {/* دائرة السكور + المستوى */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 3, mt: 1, mb: 2 }}>
          <ScoreCircle value={score} size={136} strokeWidth={12} />
          <Box>
            <Typography variant="body2" sx={{ opacity: 0.7 }}>
              Matching Score
            </Typography>
            <Typography variant="h4" sx={{ lineHeight: 1, mt: 0.5 }}>
              {Math.round(score)}%
            </Typography>
            <Chip
              label={level}
              color={chipColor}
              size="small"
              sx={{ mt: 1.5, fontWeight: 600, letterSpacing: 0.2 }}
            />
          </Box>
        </Box>

        {/* الأقسام القديمة كما هي */}
        {hasFast && (
          <>
            <Typography sx={{ mt: 2 }}>
              <strong>Suggested Skills:</strong>
            </Typography>
            <ul>
              {analysis.suggestions.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </>
        )}

        {hasLLM && (
          <>
            {Array.isArray(analysis.reasons) && analysis.reasons.length > 0 && (
              <>
                <Typography sx={{ mt: 2 }}>
                  <strong>Reasons:</strong>
                </Typography>
                <ul>
                  {analysis.reasons.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </>
            )}

            {Array.isArray(analysis.missing_skills) && analysis.missing_skills.length > 0 && (
              <>
                <Typography sx={{ mt: 2 }}>
                  <strong>Missing Skills:</strong>
                </Typography>
                <ul>
                  {analysis.missing_skills.map((m, i) => (
                    <li key={i}>{m}</li>
                  ))}
                </ul>
              </>
            )}

            {Array.isArray(analysis.nice_to_have) && analysis.nice_to_have.length > 0 && (
              <>
                <Typography sx={{ mt: 2 }}>
                  <strong>Nice to Have:</strong>
                </Typography>
                <ul>
                  {analysis.nice_to_have.map((n, i) => (
                    <li key={i}>{n}</li>
                  ))}
                </ul>
              </>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}
