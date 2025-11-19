// src/components/ActionsBar.jsx
import { Box, Button, ButtonGroup, CircularProgress, Stack, Tooltip } from "@mui/material";
import ArrowBackRoundedIcon from "@mui/icons-material/ArrowBackRounded";
import ArrowForwardRoundedIcon from "@mui/icons-material/ArrowForwardRounded";
import SaveRoundedIcon from "@mui/icons-material/SaveRounded";
import SmartToyRoundedIcon from "@mui/icons-material/SmartToyRounded";
import BoltRoundedIcon from "@mui/icons-material/BoltRounded";
import PictureAsPdfRoundedIcon from "@mui/icons-material/PictureAsPdfRounded";
import { getToken } from "../api"; // ✅ نستخدمه لتحديد حالة الدخول

export default function ActionsBar({
  activeStep,
  back,
  next,
  uploading,
  onSave,
  onAnalyze,
  onDownload,
  analyzing,
  onAnalyzeFast,
  generating, // مهم: يجي من useCvForm
}) {
  const isLast = activeStep === 3;
  const disabledAll = uploading || analyzing || generating;

  // ✅ هل المستخدم عامل تسجيل دخول؟
  const authed = !!getToken();

  return (
    <Stack spacing={2} sx={{ mt: 3 }}>
      {/* الصفّ العلوي: تنقّل */}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1.5,
          justifyContent: "space-between",
          flexWrap: "wrap",
        }}
      >
        <Button
          type="button"
          variant="outlined"
          startIcon={<ArrowBackRoundedIcon />}
          onClick={back}
          disabled={activeStep === 0 || disabledAll}
          sx={{ borderRadius: 2 }}
        >
          Back
        </Button>

        {isLast ? (
          // ✅ زر الحفظ يتعطّل إذا المستخدم غير مسجّل، مع Tooltip توضيحي
          <Tooltip title={authed ? "" : "Sign in to save your CV"} placement="top">
            {/* ملاحظة: span ضرورية لأن Tooltip ما يشتغل مباشرة على عناصر disabled */}
            <span>
              <Button
                type="button"
                variant="contained"
                color="primary"
                endIcon={<SaveRoundedIcon />}
                onClick={onSave}
                disabled={disabledAll || !authed}
                sx={{ borderRadius: 2, minWidth: 140 }}
              >
                Save CV
              </Button>
            </span>
          </Tooltip>
        ) : (
          <Button
            type="button"
            variant="contained"
            color="primary"
            endIcon={<ArrowForwardRoundedIcon />}
            onClick={next}
            disabled={disabledAll}
            sx={{ borderRadius: 2, minWidth: 120 }}
          >
            Next
          </Button>
        )}
      </Box>

      {/* الصفّ السفلي: يظهر فقط بالخطوة الأخيرة */}
      {isLast && (
        <Box
          sx={{
            display: "flex",
            gap: 1.5,
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
          }}
        >
          {/* مجموعة أزرار التحليل */}
          <ButtonGroup
            variant="contained"
            sx={{
              borderRadius: 2,
              overflow: "hidden",
              "& .MuiButton-root": { py: 1.1, px: 2, minWidth: 170, textTransform: "none" },
            }}
            disableElevation
          >
            <Tooltip title="LLM (Ollama/LLaMA) – أدق لكن أبطأ قليلاً">
              <span>
                <Button
                  type="button"
                  color="success"
                  onClick={onAnalyze}
                  disabled={disabledAll}
                  startIcon={<SmartToyRoundedIcon />}
                >
                  {analyzing ? (
                    <>
                      Analyzing…
                      <CircularProgress size={16} sx={{ ml: 1 }} />
                    </>
                  ) : (
                    "Analyze (AI)"
                  )}
                </Button>
              </span>
            </Tooltip>

            <Tooltip title="تحليل سريع بالـembeddings">
              <span>
                <Button
                  type="button"
                  color="info"
                  onClick={onAnalyzeFast}
                  disabled={disabledAll}
                  startIcon={<BoltRoundedIcon />}
                >
                  {analyzing ? (
                    <>
                      Working…
                      <CircularProgress size={16} sx={{ ml: 1 }} />
                    </>
                  ) : (
                    "Fast Analyze"
                  )}
                </Button>
              </span>
            </Tooltip>
          </ButtonGroup>

          {/* زر تحميل PDF */}
          <Button
            type="button"
            variant="outlined"
            color="secondary"
            onClick={onDownload}
            disabled={disabledAll}
            startIcon={
              generating ? (
                <CircularProgress size={16} sx={{ mr: 0.5 }} />
              ) : (
                <PictureAsPdfRoundedIcon />
              )
            }
            sx={{
              borderRadius: 2,
              minWidth: { xs: "100%", sm: 180 },
              mt: { xs: 1.5, sm: 0 },
            }}
          >
            {generating ? "Generating…" : "Download PDF"}
          </Button>
        </Box>
      )}
    </Stack>
  );
}
