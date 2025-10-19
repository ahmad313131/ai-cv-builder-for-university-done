// src/hooks/useCvForm.js
import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { API_BASE, uploadPhoto, saveCV, analyzeCV, generateCV } from "../api";

export default function useCvForm() {
  // ---------------- Steps ----------------
  const [activeStep, setActiveStep] = useState(0);
  const next = useCallback(() => setActiveStep((s) => Math.min(s + 1, 3)), []);
  const back = useCallback(() => setActiveStep((s) => Math.max(s - 1, 0)), []);

  // ---------------- Form ----------------
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    education: "",
    experience: "",
    skills: "",
    github: "",
    linkedin: "",
    languages: "",
    hobbies: "",
    photo_path: "",
    job_description: "",
  });

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  }, []);

  // ---------------- Photo upload ----------------
  const [photoPreview, setPhotoPreview] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");

  // cleanup preview URL
  useEffect(() => {
    return () => {
      if (photoPreview) URL.revokeObjectURL(photoPreview);
    };
  }, [photoPreview]);

  const handlePhotoChange = useCallback(
    async (e) => {
      const file = e.target.files?.[0];
      if (!file) return;

      const ALLOWED_TYPES = ["image/jpeg", "image/png"];
      const MAX_BYTES = 2 * 1024 * 1024;

      if (!ALLOWED_TYPES.includes(file.type)) {
        setUploadError("Only JPG/PNG images are allowed.");
        e.target.value = "";
        return;
      }
      if (file.size > MAX_BYTES) {
        setUploadError("Max file size is 2MB.");
        e.target.value = "";
        return;
      }
      setUploadError("");

      if (photoPreview) URL.revokeObjectURL(photoPreview);
      const previewUrl = URL.createObjectURL(file);
      setPhotoPreview(previewUrl);

      setUploading(true);
      try {
        const json = await uploadPhoto(file); // { path }
        setFormData((p) => ({ ...p, photo_path: json.path }));
      } catch (err) {
        setUploadError(err.message || "Upload failed.");
        setFormData((p) => ({ ...p, photo_path: "" }));
      } finally {
        setUploading(false);
        if (e.target) e.target.value = "";
      }
    },
    [photoPreview]
  );

  const photoUrl =
    photoPreview ||
    (formData.photo_path ? `${API_BASE}${formData.photo_path}` : "");

  // ---------------- Analyze (LLM + fallback) ----------------
  const [useLLM, setUseLLM] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzeError, setAnalyzeError] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const runningRef = useRef(false); // يمنع النداء المزدوج للتحليل فقط

  const callAnalyzeLLM = useCallback(async (payload) => {
    const res = await fetch(`${API_BASE}/api/llm_analyze_cv`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `LLM analyze failed (${res.status})`);
    }
    return res.json();
  }, []);

  const analyze = useCallback(async () => {
    if (runningRef.current) return;
    runningRef.current = true;
    setAnalyzeError("");
    setAnalyzing(true);
    try {
      const payload = {
        ...formData,
        job_description: formData.job_description || "",
      };
      let data;
      if (useLLM) {
        try {
          data = await callAnalyzeLLM(payload);
        } catch (e) {
          console.warn("LLM failed, falling back to fast:", e);
          data = await analyzeCV(payload); // fallback
        }
      } else {
        data = await analyzeCV(payload);
      }
      setAnalysis(data);
    } catch (e) {
      setAnalyzeError(e.message || "Analyze failed");
    } finally {
      setAnalyzing(false);
      runningRef.current = false;
    }
  }, [formData, useLLM, callAnalyzeLLM]);

  const analyzeFast = useCallback(async () => {
    if (analyzing || runningRef.current) return;
    runningRef.current = true;
    setAnalyzeError("");
    setAnalyzing(true);
    try {
      const payload = {
        ...formData,
        job_description: formData.job_description || "",
      };
      const data = await analyzeCV(payload);
      setAnalysis(data);
    } catch (e) {
      setAnalyzeError(e.message || "Fast analyze failed");
    } finally {
      setAnalyzing(false);
      runningRef.current = false;
    }
  }, [formData, analyzing]);

  // ---------------- Save ----------------
  const submitCV = useCallback(async () => {
    const data = await saveCV(formData);
    return data;
  }, [formData]);

  // ---------------- Generate / Download PDF ----------------
  const [generating, setGenerating] = useState(false);
  const abortRef = useRef(null);

  const downloadPdf = useCallback(async () => {
    setGenerating(true);
    try {
      abortRef.current = new AbortController();
      // backend يعيد blob مباشرة؛ لا نلفّه داخل Blob جديد
      const blob = await generateCV(formData); // ENDPOINTS.pdf
      const url = window.URL.createObjectURL(blob);
      const safe = (formData.name || "CV").replace(/[\\/:*?"<>|]+/g, "_");
      const a = document.createElement("a");
      a.href = url;
      a.download = `${safe}_AI.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      // فيك تعرض Toast/Alert من فوق؛ هون بس منرمي الخطأ للي بينادي إذا احتاج
      console.error("Download failed:", e);
      throw e;
    } finally {
      setGenerating(false);
    }
  }, [formData]);

  const cancelGenerate = useCallback(() => {
    abortRef.current?.abort();
    setGenerating(false);
  }, []);

  // ---------------- Expose ----------------
  return useMemo(
    () => ({
      // steps
      activeStep,
      setActiveStep,
      next,
      back,
      // form
      formData,
      setFormData,
      handleChange,
      handlePhotoChange,
      photoUrl,
      uploading,
      uploadError,

      // analyze
      useLLM,
      setUseLLM,
      analyzing,
      analyzeError,
      analysis,
      analyze,
      analyzeFast,

      // save
      submitCV,

      // pdf
      downloadPdf,
      generating,
      cancelGenerate,
    }),
    [
      activeStep,
      next,
      back,
      formData,
      handleChange,
      handlePhotoChange,
      photoUrl,
      uploading,
      uploadError,
      useLLM,
      analyzing,
      analyzeError,
      analysis,
      analyze,
      analyzeFast,
      submitCV,
      downloadPdf,
      generating,
      cancelGenerate,
    ]
  );
}
