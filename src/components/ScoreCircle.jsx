// src/components/ScoreCircle.jsx
import React from "react";

export default function ScoreCircle({
  value = 0,        // 0..100
  size = 140,       // القطر بالبكسل
  strokeWidth = 12, // سماكة الدائرة
  showLabel = true, // إظهار الرقم % بالنص
}) {
  const clamped = Math.max(0, Math.min(100, Number(value) || 0));
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - clamped / 100);

  // تدرّج لون HSL: 0 (أحمر) → 120 (أخضر)
  const hue = (clamped * 120) / 100;
  const strokeColor = `hsl(${hue} 85% 45%)`;

  return (
    <svg width={size} height={size} style={{ display: "block" }}>
      <defs>
        {/* ظل ناعم للدائرة الخلفية */}
        <filter id="softShadow" x="-50%" y="-50%" width="200%" height="200%">
          <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.2" />
        </filter>
      </defs>

      {/* الخلفية الرمادية الخفيفة */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        stroke="#e6e6e9"
        strokeWidth={strokeWidth}
        fill="none"
        filter="url(#softShadow)"
      />

      {/* الدائرة الملوّنة (قابلة للتعبئة) */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        stroke={strokeColor}
        strokeWidth={strokeWidth}
        fill="none"
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        style={{
          transform: "rotate(-90deg)",
          transformOrigin: "50% 50%",
          transition: "stroke-dashoffset 600ms ease, stroke 300ms ease",
        }}
      />

      {/* النص بالوسط */}
      {showLabel && (
        <text
          x="50%"
          y="50%"
          dominantBaseline="central"
          textAnchor="middle"
          fontFamily="Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
          fontWeight="700"
          fontSize={size * 0.22}
          fill="#1f2937"
        >
          {Math.round(clamped)}%
        </text>
      )}
    </svg>
  );
}
